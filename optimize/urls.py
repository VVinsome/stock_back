from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from optimize import views

urlpatterns = [
    path('optimize/<stocks_csv>/', views.Optimize.as_view()),
    ]