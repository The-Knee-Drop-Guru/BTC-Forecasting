from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('forecast/', views.forecast, name='forecast'),
]