import logging
from time import sleep

from django.core.management.base import BaseCommand

from inventory.models import EbayItem, SystemId

logger = logging.getLogger(__name__)

intake = """
# TODO - fill in import from Google Sheets
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Importing items")
        for line in intake.split("\n"):
            if not line:
                continue

            system_id, title, url = line.split("\t")

            orderId = url.split("orderId=")[1].split("&")[0]

            try:
                item = EbayItem.objects.get(order_id=orderId)
                sys_id = SystemId.objects.get(pk=system_id)
                item.system_id = sys_id
                item.save()
            except EbayItem.DoesNotExist:
                print("Cant find item with orderId", orderId)
                continue
            print(f"Creating item {title} with id {system_id} and orderId {orderId}")
