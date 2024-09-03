import asyncio

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
                transaction = api.get_item_transactions(item_id)
                order_id = transaction["GetItemTransactionsResponse"]["TransactionArray"]["Transaction"][
                    "ExtendedOrderID"]

                yield f"event: log\ndata: Adding item {item_id} with order {order_id}<br />\n\n"
                await EbayItem.objects.aupdate_or_create(
                    item_id=item_id,
                    order_id=order_id,
                    title=purchase["Transaction"]["Item"]["Title"],
                    bought_price=float(purchase["Transaction"]["TotalTransactionPrice"]["#text"]),
                    bought_date=purchase["Transaction"]["PaidTime"],
                    user=request.user
                )
            except Exception as e:
                yield f"event: log\ndata: Failed to add item {item_id}: {e}<br />\n\n"

        yield f"event: log\ndata: Done processing {len(purchases.items())}<br />\n\n"
        yield f"event: done\ndata: true\n\n"

    response = StreamingHttpResponse(stream())
    response['Content-Type'] = 'text/event-stream'
    return response
