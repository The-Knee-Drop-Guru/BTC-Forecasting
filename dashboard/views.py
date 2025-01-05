from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Forecast, Feature, User, UserProfile, Sentiment
from .forms import SignUpForm

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
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"환영합니다, {username}님!")
                return redirect('/')
            else:
                messages.error(request, "로그인에 실패했습니다. 사용자 이름 또는 비밀번호를 확인하세요.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

from django.contrib.auth import login

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            # 중복 확인
            if User.objects.filter(username=username).exists():
                messages.error(request, "이미 사용 중인 아이디입니다.")
                return render(request, 'dashboard/signup.html', {'form': form})

            if User.objects.filter(email=email).exists():
                messages.error(request, "이미 등록된 이메일입니다.")
                return render(request, 'dashboard/signup.html', {'form': form})

            user = form.save()

            # 로그인 시 backend 지정
            backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend=backend)

            messages.success(request, f"환영합니다, {user.username}님!")
            return redirect('dashboard:index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()
    return render(request, 'dashboard/signup.html', {'form': form})



# 비트코인 가격 변동 그래프를 위한 뷰
def forecast(request):
    data = Forecast.objects.all()
    response = {
        "time": [entry.date_time.strftime('%Y-%m-%d %H:%M') for entry in data],
        "real_price": [entry.real_price for entry in data],
        "predicted_price": [entry.predicted_price if entry.predicted_price else None for entry in data],
    }
    return JsonResponse(response)