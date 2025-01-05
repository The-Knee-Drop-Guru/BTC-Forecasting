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
    path('forecast/', views.forecast, name='forecast'),
]