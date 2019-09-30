from rest_framework import serializers

from .models import Stock, Price


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer): 
    prices = PriceSerializer(many=True, required=False)

    class Meta:
        model = Stock
        fields = '__all__'
