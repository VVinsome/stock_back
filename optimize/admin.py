from django.contrib import admin

from .models import Stock, Price
# Register your models here.

admin.site.register(Stock)
admin.site.register(Price)
