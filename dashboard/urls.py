from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('api/btc-forecasting/', views.btc_forecasting_api, name='btc_forecasting_api'),  # 비트코인 예측 데이터
    path('api/feature-importance/', views.feature_importance_api, name='feature_importance_api'),  # 피처 중요도 데이터
]