import logging

import requests
from django.contrib.auth.models import AbstractUser
from django.db import models

import settings
from inventory.utils.ebay import GET_ACCOUNT_REQUEST, TradingApi

import logging

log = logging.getLogger(__name__)


class BadRefreshToken(Exception):
    pass


class SystemId(models.Model):
    id = models.AutoField(primary_key=True)


class EbayItem(models.Model):
    item_id = models.CharField(max_length=255, primary_key=True)
    order_id = models.CharField(max_length=255)
    system_id = models.ForeignKey("SystemId", on_delete=models.SET_NULL, null=True)
    system_title = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255)
    bought_price = models.FloatField()
    bought_date = models.DateTimeField()
    gross_profit = models.FloatField(null=True)
    bought_tracking_number = models.CharField(max_length=255, null=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    class State(models.TextChoices):
        IN_FLIGHT = "IN_FLIGHT", "in flight"
        ON_SHELF = "ON_SHELF", "on shelf"
        ON_SHELF_LISTED = "ON_SHELF_LISTED", "listed"
        SHIPPED = "SHIPPED", "shipped"

    state = models.CharField(max_length=255, choices=State.choices, default=State.IN_FLIGHT)

    def order_id_url(self):
        return f"https://order.ebay.com/ord/show?orderId={self.order_id}#/"

    def net_profit(self):
        if self.gross_profit is None:
            return None
        return self.gross_profit - self.bought_price


class User(AbstractUser):
    ebay_token = models.CharField(max_length=255, null=True)
    ebay_refresh_token = models.CharField(max_length=255, null=True)

    def is_token_valid(self):
        api = TradingApi(self.ebay_token)
        try:
            r = api.get_account()
        except Exception as e:
            log.error(f"Failed to check token expiration: {e}")
            return False

        if '<Ack>Success</Ack>' in r.text:
            return True
        return False

    def refresh_ebay_token(self):
        if not self.ebay_refresh_token:
            raise BadRefreshToken("No refresh token")

        data = f"grant_type=refresh_token&refresh_token={self.ebay_refresh_token}&scope={settings.EBAY_SCOPES}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {settings.EBAY_CLIENT_SECRET}"
        }

        response = requests.post("https://api.ebay.com/identity/v1/oauth2/token", headers=headers, data=data)
        response.raise_for_status()

        self.ebay_token = response.json()['access_token']
        self.save()
