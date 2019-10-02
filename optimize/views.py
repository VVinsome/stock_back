from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import django.utils.dateparse
from django.conf import settings

import numpy as np 
import pandas as pd 
from scipy.optimize import minimize
import sys


# Create your views here.

from rest_framework import status


from .models import Stock, Price
from .serializers import StockSerializer, PriceSerializer

import datetime
import holidays
from ratelimit import limits, sleep_and_retry
import requests


URL = settings.URL
token = settings.TOKEN
symbols = 'ref-data/iex/symbols'
PARAMS = {'token':token,'chartCloseOnly':'true'}
ONE_MINUTE = 60
ONE_DAY = datetime.timedelta(days=1)
HOLIDAYS_US = holidays.US()


def last_business_day():
    business_day = datetime.date.today()
    while business_day.weekday() in holidays.WEEKEND or business_day in HOLIDAYS_US:
        business_day -= ONE_DAY
    return business_day

@sleep_and_retry
@limits(calls=99, period=ONE_MINUTE)
def call_api(Url,Params):
    response = requests.get(url=Url,params=Params,timeout=5)
    return response

class Equity():
    def __init__(self,name,price_list):
        self.name = name
        self.price_list = price_list

    def get_dataframe(self):
        log_price = np.log(self.price_list) 
        df = pd.DataFrame({'log_price':log_price})
        df['log_return'] = df['log_price'].diff()
        df = df.dropna()
        return df

#TODO make API CALLS INSTEAD if not IN DATABASE
class Optimize(APIView):

 
    def findOptimalWeight(self,equity_list,cov_matrix,mean_list):
        leng = len(equity_list)
        x = np.ones(leng)/leng
        mean = mean_list
        sigma = cov_matrix

        #minimize inverse of Sharpe Ratio 
        def target(x, sigma, mean):
            if x.dot(mean) == 0:
                return float(sys.maxsize)
            sr_inv = (np.sqrt(np.dot(np.dot(x.T,sigma),x)*252))/abs((x.dot(mean))*252)
            return sr_inv

        c = ({'type':'eq','fun':lambda x: sum(x) - 1})
        bounds = [(0,1) for i in range(leng)]
        res = minimize(target, x, args = (sigma,mean),method = 'SLSQP',constraints = c,bounds = bounds)
        opt_weight = res.x
        return opt_weight
    
    def get(self,request,stocks_csv):
        if stocks_csv == '':
            return Response('No symbols found', status=status.HTTP_404_NOT_FOUND)
        stocks_parsed = stocks_csv.split(',')
        stocks_in = Stock.objects.filter(symbol__in=stocks_parsed)
        def fun(x):
            s_in = [str(x) for x in list(stocks_in)]
            if x not in s_in:
                return True
            else:
                return False
        stocks_not_in = list(filter(fun, stocks_parsed))
        Stock_list = []
        Price_list = []
        #TODO refactor so that call api is just determined by if condition
        for s in stocks_not_in:
            res = call_api('{URL}{sy}/chart/'.format(URL=URL,sy=s),PARAMS)
            s_hist = res.json()
            st = Stock.objects.create(symbol=s)
            Stock_list.append(st)
            for i in s_hist:
                Price_list.append(Price(close_price=i['close'],date= django.utils.dateparse.parse_date(i['date']),stock=st))
        for n in stocks_in:
            if n.prices.last().date == last_business_day():
                continue
            delta = last_business_day() - n.prices.first().date
            res = call_api('{URL}{sy}/chart/'.format(URL=URL,sy=n),{**PARAMS,'chartLast':delta.days})
            s_hist = res.json()
            for i in s_hist:
                Price_list.append(Price(close_price=i['close'],date= django.utils.dateparse.parse_date(i['date']),stock=n))
        Price.objects.bulk_create(Price_list)
        stocks = Stock.objects.filter(symbol__in=stocks_parsed)
        equity_list = []
        mean_list = []
        for item in stocks:
            if(item.prices.all()[:20].count() == 20):
                equity_list.append(Equity(item.symbol,list(item.prices.all()[:20].values_list('close_price',flat=True))))
            else:
                return  Response('{symb} does not have enough historical data'.format(symb=item.symbol), status=status.HTTP_409_CONFLICT)
        for equity in equity_list:
            equity.df = equity.get_dataframe()
            equity.mean = np.mean(equity.df['log_return'])
            equity.std = np.std(equity.df['log_return'])
            mean_list.append(equity.mean)
        cov_matrix = np.cov([e.df['log_return'] for e in equity_list])
        optimal_weights = self.findOptimalWeight(equity_list,cov_matrix,mean_list)
        jsonDict = {equity.name: {'weight': round(weight,4), 'single_exp_return':round(equity.mean,5),'std':round(equity.std,5)} for equity,weight in zip(equity_list,optimal_weights)}
        jsonDict['exp_return'] = np.dot(mean_list,optimal_weights) * 252
        jsonDict['stdev'] = np.sqrt(np.dot(np.dot(optimal_weights.T,cov_matrix),optimal_weights)*252)
        return Response(jsonDict)
            


        

