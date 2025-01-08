from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('login/', auth_views.LoginView.as_view(
        template_name='dashboard/login.html',
        authentication_form=CustomLoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='dashboard:index'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('simulation/', views.simulation, name='simulation'),
    path('api/btc-forecasting/', views.btc_forecasting_api, name='btc_forecasting_api'),  # 비트코인 예측 데이터
    path('api/error-data/', views.error_data_api, name='error_data_api'), # 비트코인 에러 데이터
    path('api/feature-importance/', views.feature_importance_api, name='feature_importance_api'),  # 피처 중요도 데이터
    path('api/sentiment/<str:class_id>/', views.sentiment_data_api, name='sentiment_data_api'),  # 감정 분석 데이터
]