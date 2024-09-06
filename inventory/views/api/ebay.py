import asyncio

from asgiref.sync import sync_to_async
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse

from inventory.models import EbayItem, User, SystemId
from inventory.utils.ebay import TradingApi

import logging

log = logging.getLogger(__name__)


@login_required
def assign_system_id(request, pk=None):
    item = EbayItem.objects.get(item_id=pk)
    item.system_id = SystemId.objects.create()
    item.save()

    return HttpResponse(item.system_id)


@login_required
def refresh_token(request):
    if request.user.is_token_valid():
        return HttpResponse("Cached token is still valid")

    try:
        request.user.refresh_ebay_token()
        return HttpResponse("Token refreshed")
    except Exception as e:
        return HttpResponse(f"Failed to refresh token: {e}", status=400)


@login_required
async def refresh_item(request, pk=None):
    user = await request.auser()
    api = TradingApi(user.ebay_token)

    purchases = api.get_purchases()

    for item_id, purchase in purchases.items():
        if item_id != pk:
            continue

        await update_item(api, request.user, item_id, purchase)

    return HttpResponse("Done")


async def update_item(api, user, item_id, purchase):
    transaction = api.get_item_transactions(item_id)
    t = transaction["GetItemTransactionsResponse"]["TransactionArray"]["Transaction"]
    order_id = t["ExtendedOrderID"]
    try:
        tracking_number = t["ShippingDetails"]["ShipmentTrackingDetails"]["ShipmentTrackingNumber"]
    except TypeError:
        tracking_number = t["ShippingDetails"]["ShipmentTrackingDetails"][0]["ShipmentTrackingNumber"]
    except KeyError:
        # not available yet
        tracking_number = None

    vals = {
        "item_id": item_id,
        "order_id": order_id,
        "title": purchase["Transaction"]["Item"]["Title"],
        "bought_date": purchase["Transaction"]["PaidTime"],
        "bought_tracking_number": tracking_number,
        "user": user
    }

    try:
        item = await EbayItem.objects.aget(item_id=item_id)
        item.__dict__.update(vals)
        await item.asave()
    except EbayItem.DoesNotExist:
        # only update the vals if its not set: sometimes we do custom pricing (like for bundles), and dont
        # want this value overwritten
        vals["bought_price"] = float(t["MonetaryDetails"]["Payments"]["Payment"]["PaymentAmount"]["#text"])
        await EbayItem.objects.acreate(**vals)


def stream_log(msg):
    return f"event: log\ndata: {msg}<br />\n\n"


def close_stream_log():
    return f"event: done\ndata: true\n\n"


@login_required
def refresh_sales(request):
    async def stream():
        user = await request.auser()
        api = TradingApi(user.ebay_token)

        yield stream_log("Getting sales...")
        sales = api.get_sales()
        yield stream_log("Getting sales...done")

        for sale in sales["orders"]:
            if len(sale["lineItems"]):
                line_item = sale["lineItems"][0]
                sku = line_item["sku"]
                parts = sku.split("-")
                system_id = parts[0]
                system_id = system_id.replace("id", "")
                if system_id == "":
                    yield stream_log(f"Skipping order {sale['orderId']}, no sku ({sku})")
                    continue
                yield stream_log(f"Updating sku item {system_id}")
                try:
                    item = await EbayItem.objects.exclude(state=EbayItem.State.SHIPPED).aget(system_id=system_id)
                except EbayItem.DoesNotExist:
                    yield stream_log(f"Skipping order {sale['orderId']}, no item with system_id {system_id}")
                    continue
                item.state = EbayItem.State.SHIPPED
                item.gross_profit = float(sale["paymentSummary"]["totalDueSeller"]["value"])
                await item.asave()
            else:
                yield stream_log(f"Skipping order {sale['orderId']}, no line item")

        yield close_stream_log()

    response = StreamingHttpResponse(stream())
    response['Content-Type'] = 'text/event-stream'
    return response


@login_required
def refresh_purchases(request):
    async def stream():

        # # if not request.user.is_token_valid():
        # #     request.user.refresh_ebay_token()
        #
        # for i in range(5):
        #     yield f"data: Hello {i}\n\n"
        #     await asyncio.sleep(1)
        api = TradingApi(request.user.ebay_token)

        yield "event: log\ndata: Getting purchases...<br />\n\n"
        purchases = api.get_purchases()
        yield "event: log\ndata: Getting purchases...done<br />\n\n"

        for item_id, purchase in purchases.items():
            try:
                yield f"event: log\ndata: Adding item {item_id}<br />\n\n"
                await update_item(api, request.user, item_id, purchase)
            except Exception as e:
                yield f"event: log\ndata: Failed to add item {item_id}: {e}<br />\n\n"

        yield f"event: log\ndata: Done processing {len(purchases.items())}<br />\n\n"
        yield f"event: done\ndata: true\n\n"

    response = StreamingHttpResponse(stream())
    response['Content-Type'] = 'text/event-stream'
    return response
