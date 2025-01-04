from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Forecast, Feature, User, UserProfile, Sentiment

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