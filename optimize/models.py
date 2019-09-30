from django.db import models
# Create your models here.

class Stock(models.Model):
    symbol = models.CharField(max_length=30,unique=True)
    

    def __str__(self):
        return self.symbol

class Price(models.Model):
    close_price = models.FloatField()
    date = models.DateField()
    stock = models.ForeignKey(Stock, related_name='prices',on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return 'price: {price}, date = {date}'.format(price = self.close_price, date = self.date)
