import requests
import xmltodict

GET_ACCOUNT_REQUEST = """
        <?xml version="1.0" encoding="utf-8"?>
<GetAccountRequest xmlns="urn:ebay:apis:eBLBaseComponents">    
	<ErrorLanguage>en_US</ErrorLanguage>
	<WarningLevel>Low</WarningLevel>
  <AccountEntrySortType>AccountEntryFeeTypeAscending</AccountEntrySortType>
  <AccountHistorySelection>LastInvoice</AccountHistorySelection>
</GetAccountRequest>"""

GET_ITEM_TRANSACTIONS = lambda token, item_id: f"""
<?xml version="1.0" encoding="utf-8"?>
<GetItemTransactionsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{token}</eBayAuthToken>
  </RequesterCredentials>
	<ErrorLanguage>en_US</ErrorLanguage>
	<WarningLevel>High</WarningLevel>
  <ItemID>{item_id}</ItemID>
</GetItemTransactionsRequest>
"""

GET_PURCHASES_REQUEST = lambda token: f"""
<?xml version="1.0" encoding="utf-8"?>
<GetMyeBayBuyingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{token}</eBayAuthToken>
  </RequesterCredentials>
	<ErrorLanguage>en_US</ErrorLanguage>
	<WarningLevel>High</WarningLevel>
  <DetailLevel>ReturnAll</DetailLevel>
  <BuyingSummary>
    <Include>true</Include>
  </BuyingSummary>
</GetMyeBayBuyingRequest>
"""


class TradingApi:
    def __init__(self, token):
        self._token = token

    def _get(self, call_name, data):
        r = requests.post("https://api.ebay.com/ws/api.dll", data=data, headers={
            "X-EBAY-API-CALL-NAME": call_name,
            "X-EBAY-API-IAF-TOKEN": self._token,
            "X-EBAY-API-SITEID": "0",
            "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        })
        r.raise_for_status()
        return r

    def get_item_transactions(self, item_id):
        r = requests.post("https://api.ebay.com/ws/api.dll", data=GET_ITEM_TRANSACTIONS(self._token, item_id), headers={
            "X-EBAY-API-CALL-NAME": "GetItemTransactions",
            "X-EBAY-API-SITEID": "0",
            "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        })
        r.raise_for_status()
        return xmltodict.parse(r.text)

    def get_purchases(self):
        r = requests.post("https://api.ebay.com/ws/api.dll", data=GET_PURCHASES_REQUEST(self._token), headers={
            "X-EBAY-API-CALL-NAME": "GetMyeBayBuying",
            "X-EBAY-API-IAF-TOKEN": self._token,
            "X-EBAY-API-SITEID": "0",
            "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        })
        r.raise_for_status()

        purchases = xmltodict.parse(r.text)

        i = {}
        for purchase in purchases['GetMyeBayBuyingResponse']['WonList']['OrderTransactionArray']['OrderTransaction']:
            item_id = purchase['Transaction']['Item']['ItemID']
            i[item_id] = purchase

        return i

    def get_sales(self):
        r = requests.get("https://api.ebay.com/sell/fulfillment/v1/order", headers={
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        })
        r.raise_for_status()
        return r.json()

    def get_account(self):
        r = requests.post("https://api.ebay.com/ws/api.dll", data=GET_ACCOUNT_REQUEST, headers={
            "X-EBAY-API-CALL-NAME": "GetAccount",
            "X-EBAY-API-IAF-TOKEN": self._token,
            "X-EBAY-API-SITEID": "0",
            "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        })
        r.raise_for_status()
        return r
