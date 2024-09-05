import asyncio

from asgiref.sync import sync_to_async
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse

from inventory.models import EbayItem, User
from inventory.utils.ebay import TradingApi

import logging

log = logging.getLogger(__name__)


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

    item, _ = await EbayItem.objects.aupdate_or_create(item_id=item_id)

    vals = {
        "order_id": order_id,
        "title": purchase["Transaction"]["Item"]["Title"],
        "bought_date": purchase["Transaction"]["PaidTime"],
        "bought_tracking_number": tracking_number,
        "user": user
    }

    if not item.bought_price:
        # only update the vals if its not set: sometimes we do custom pricing (like for bundles), and dont
        # want this value overwritten
        vals["bought_price"] = float(t["MonetaryDetails"]["Payments"]["Payment"]["PaymentAmount"]["#text"]),

    item.__dict__.update(vals)
    await item.asave()


def stream_log(msg):
    yield f"event: log\ndata: {msg}<br />\n\n"


def close_stream_log():
    yield f"event: done\ndata: true\n\n"


@login_required
def refresh_sales(request):
    async def stream():

        import pdb;pdb.set_trace()
        user = await request.auser()
        api = TradingApi(user.ebay_token)

        pass

        # stream_log("Getting sales...")
        # sales = api.get_sales()
        # stream_log("Getting sales...done")
        #
        #
        # for sale in sales["orders"]:
        #     if len(sale["lineItems"]):
        #         line_item = sale["lineItems"][0]
        #         sku = line_item["sku"]
        #         system_id, _ = sku.split("-")
        #         system_id = system_id.replace("id", "")
        #         if system_id == "":
        #             stream_log(f"Skipping order {sale['orderId']}, no sku ({sku})")
        #             continue
        #         stream_log(f"Updating sku item {system_id}")
        #         item = await EbayItem.objects.afilter(state=EbayItem.State.ON_SHELF_LISTED).aget(system_id=system_id)
        #         item.state = EbayItem.State.SHIPPED
        #         item.net_profit = float(sale["paymentSummary"]["totalDueSeller"]["value"])
        #         await item.asave()
        #     else:
        #         stream_log(f"Skipping order {sale['orderId']}, no line item")
        #
        #     close_stream_log()

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
        user = await request.auser()
        api = TradingApi(user.ebay_token)

        stream_log("Getting purchases...")
        purchases = api.get_purchases()
        stream_log("Getting purchases...done")

        for item_id, purchase in purchases.items():
            try:
                await update_item(api, request.user, item_id, purchase)
                stream_log(f"Adding item {item_id}")
            except Exception as e:
                stream_log(f"Failed to add item {item_id}: {e}")

        stream_log(f"Done processing {len(purchases.items())}")
        close_stream_log()

    response = StreamingHttpResponse(stream())
    response['Content-Type'] = 'text/event-stream'
    return response
