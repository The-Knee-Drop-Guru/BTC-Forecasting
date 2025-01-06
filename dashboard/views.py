from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Forecast, Feature, User, UserProfile, Sentiment
from .forms import SignUpForm
from rest_framework.response import Response
from rest_framework.decorators import api_view

# 대시보드 화면을 위한 뷰
def dashboard(request):
    # 예측 결과 가져오기 
    forecasts = Forecast.objects.all()
    
    # 피처 중요도 가져오기
    features = Feature.objects.all()
    
    # 감정 분석 데이터 가져오기
    sentiments = Sentiment.objects.all()
    
    # 사용자 정보 가져오기
    users = User.objects.all()
    
    # 사용자 프로필 이미지 URL 가져오기
    user_profiles = UserProfile.objects.all()
    
    # 템플릿에 데이터를 전달
    context = {
        'forecasts': forecasts,
        'features': features,
        'users': users,
        'user_profiles': user_profiles,
        'sentiments': sentiments,
    }

    return render(request, 'dashboard/index.html', context)

# 로그인화면을 위한 뷰
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"환영합니다, {user.first_name}님!")
                return redirect('dashboard:index')
            else:
                messages.error(request, "로그인 정보가 올바르지 않습니다.")
        else:
            messages.error(request, "로그인 양식을 올바르게 입력해주세요.")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

# 회원가입화면을 위한 뷰
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()  # 사용자 저장
            messages.success(request, "회원가입이 완료되었습니다. 로그인해주세요.")
            return redirect('dashboard:login')  # 회원가입 후 로그인 페이지로 리다이렉트
        else:
            messages.error(request, "회원가입에 실패했습니다. 양식을 확인해주세요.")
    else:
        form = SignUpForm()
    return render(request, 'dashboard/signup.html', {'form': form})


# 비트코인 가격 변동 데이터를 반환하는 API
@api_view(['GET'])
def btc_forecasting_api(request):
    """
    최근 360개의 비트코인 실제 가격과 예측 가격 데이터를 반환함
    데이터는 시간(time), 실제 가격(real_price), 예측 가격(predicted_price)으로 구성된 JSON 형식으로 반환됨
    """
    data = Forecast.objects.order_by('-date_time')[:540]
    response = {
        "time": [entry.date_time.strftime('%Y-%m-%d %H:%M') for entry in data],
        "real_price": [entry.real_price for entry in data],
        "predicted_price": [entry.predicted_price for entry in data],
    }
    return Response(response)

# 모델의 피처 중요도 데이터를 반환하는 API
@api_view(['GET'])
def feature_importance_api(request):
    """
    가장 최근 날짜의 피처 중요도 데이터를 반환함
    데이터는 각 피처 이름(name)과 중요도(importance)로 구성된 JSON 형식으로 반환됨
    """
    # 가장 최근 날짜의 피처 중요도 가져오기
    latest_date = Feature.objects.latest('date_time').date_time
    features = Feature.objects.filter(date_time=latest_date)
    
    # JSON 데이터로 변환
    response_data = {
        "features": [
            {"name": feature.name, "importance": feature.importance}
            for feature in features
        ]
    }
    return Response(response_data)