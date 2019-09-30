from django.test import TestCase
from .models import Stock, Price
from django.urls import reverse
from datetime import date, timedelta
import numpy as np
from .views import Optimize,Equity
import random
# Create your tests here.
def Rand(start,end,num):
    res = []
    random.seed(10)
    for j in range(num):
        res.append(float(random.randint(start,end)))
    return res
lst = Rand(50,55,30) 
lst2 = Rand(100,104,30)
lst3 = Rand(30,32,30)
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
        response = self.client.get('/optimize/AAPL,GOOG',follow=True)
        print(response.data)
        # self.assertEqual(response.data['GOOG']['weight'],1.0)
    
    def testOptimizeThreeStockView(self):
        response = self.client.get('/optimize/AAPL,GOOG,AMZN',follow=True)
        print(response.data)