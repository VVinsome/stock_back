from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

import numpy as np 
import pandas as pd 
from scipy.optimize import minimize
import sys
# Create your views here.

from rest_framework import status


from .models import Stock, Price
from .serializers import StockSerializer, PriceSerializer

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
        stocks_parsed = stocks_csv.split(',')
        stocks = Stock.objects.filter(symbol__in=stocks_parsed)
        equity_list = []
        mean_list = []
        for item in stocks:
            if(item.prices.all()[:21].count() == 21):
                equity_list.append(Equity(item.symbol,list(item.prices.all()[:21].values_list('close_price',flat=True))))
            else:
                return  Response('{symb} does not have enough historical data'.format(symb=item.symbol), status=status.HTTP_409_CONFLICT)
        for equity in equity_list:
            equity.df = equity.get_dataframe()
            equity.mean = np.mean(equity.df['log_return'])
            equity.std = np.std(equity.df['log_return'])
            #print(equity.mean,'mean')
            #print(equity.std,'std')
            mean_list.append(equity.mean)
        cov_matrix = np.cov([e.df['log_return'] for e in equity_list])
        #print('cov',cov_matrix)
        optimal_weights = self.findOptimalWeight(equity_list,cov_matrix,mean_list)
        #print('opt',optimal_weights)
        jsonDict = {equity.name: {'weight': round(weight,4), 'single_exp_return':equity.mean,'std':equity.std} for equity,weight in zip(equity_list,optimal_weights)}
        jsonDict['exp_return'] = np.dot(mean_list,optimal_weights) * 252
        #print('exp',jsonDict['exp_return'])
        jsonDict['stdev'] = np.sqrt(np.dot(np.dot(optimal_weights.T,cov_matrix),optimal_weights)*252)
        #print('std',jsonDict['stdev'])
        return Response(jsonDict)
            


        

