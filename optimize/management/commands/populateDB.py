import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
import django.utils.dateparse
from django.core.management.base import BaseCommand
from ratelimit import limits, sleep_and_retry
from django.conf import settings

import sys
sys.path.insert(0, 'optimize')
from optimize.models import Stock, Price


URL = settings.URL
token = settings.TOKEN
TEST_URL = settings.TEST_URL
TEST_token = settings.TEST_token
symbols = 'ref-data/iex/symbols'
PARAMS = {'token':token}

iex_adapter = HTTPAdapter(max_retries=5)
session = requests.Session()
session.mount(URL,iex_adapter)
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=99, period=ONE_MINUTE)
def call_api(Url,Params):
    response = requests.get(url=Url,params=Params,timeout=3)
    return response

class Command(BaseCommand):
    help = 'calls api to fill DB with stock and prices'


    def handle(self, *args, **kwargs):
        for i in range(100): 
            try:
                r = call_api(Url= URL + symbols, Params= PARAMS)
            except (requests.ConnectionError, requests.Timeout, requests.ReadTimeout):
                continue
            break
                    
        if r:
            data = r.json()
            for s in data:
                #create stock or if already made then call close price instead.
                stock, created = Stock.objects.get_or_create(symbol=s['symbol'])
                history_url = '/stock/{symbol}/chart/1m'.format(symbol=s['symbol']) if created else '/stock/{symbol}/previous'.format(symbol=s['symbol'])
                for i in range(100):
                    try:
                        res = call_api(Url=URL+history_url,Params= PARAMS)
                    except (requests.ConnectionError, requests.Timeout, requests.ReadTimeout):
                        continue
                    break
                if res:
                    pr = res.json()
                    pr = [pr] if not created else pr
                    for p in pr:
                        price = Price.objects.create(close_price =p['close'] , date= django.utils.dateparse.parse_date(p['date']), stock = stock)
