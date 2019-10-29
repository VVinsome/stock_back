from django.test import TestCase
from .models import Stock, Price
from django.urls import reverse
from datetime import date, timedelta
import numpy as np
from .views import Optimize,Equity
import random
# Create your tests here.

def createList(start,total,increment):
    res = [start + i*increment for i in range(total)]
    return res
def createRiskyList(start,total,increment):
    res = [start + i*increment if i % 10 == 0 else start - (i+1)*increment for i in range(total)]
    return res

lst = createRiskyList(400,30,-.0005)
lst2 = createList(100000,30,.001)
lst3 = createRiskyList(400,30,.002)
def create_stock(stock_name, price_list):
    stock = Stock.objects.create(symbol=stock_name)
    for i in range(len(price_list)):
        Price.objects.create(close_price= price_list[i], date=date.today() - timedelta(days=i), stock= stock )
    return stock
class StockModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_stock(stock_name='GOOG',price_list=lst2)
        create_stock(stock_name='AMZN',price_list=lst3)
        cls.stock = create_stock(stock_name='AAPL',price_list=lst)
        cls.equity = Equity(cls.stock.symbol,list(cls.stock.prices.all()[:21].values_list('close_price',flat=True)))
        cls.df = cls.equity.get_dataframe()
    

    def testCreation(self):
        self.assertTrue(self.stock.symbol == 'AAPL')
    
    def testEquityCreation(self):
        self.assertEqual(self.equity.name, 'AAPL')
        self.assertListEqual(self.equity.price_list, lst[:21])
    
    def testDataFrame(self):
        self.assertEqual(len(self.df.index), 20)

    def testOptimizeSingleStockView(self):
        response = self.client.get('/optimize/AAPL',follow=True) 
        self.assertEqual(response.data['AAPL']['weight'], 1.0)

    def testOptimizeTwoStockView(self):
        response = self.client.get('/optimize/AAPL,AMZN',follow=True)
        self.assertTrue(response.data.get('AAPL') != None)
        self.assertTrue(.4 < response.data.get('AAPL')['weight'] < .6 )
        self.assertTrue(.4 < response.data.get('AMZN')['weight'] < .6 )
  
    def testOptimizeThreeStockView(self):
        response = self.client.get('/optimize/AAPL,GOOG,AMZN',follow=True)
        self.assertTrue(response.data.get('AMZN') != None)
        self.assertTrue(.05 < response.data.get('AMZN')['weight'] < .10 )
        self.assertTrue(.30 < response.data.get('AAPL')['weight'] < .35 )
        self.assertTrue(.50 < response.data.get('GOOG')['weight'] < .60 )