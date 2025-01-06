from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
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
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"환영합니다, {username}님!")
                return redirect('/')
            else:
                # 계정이 없거나 비밀번호가 틀린 경우 처리
                if not User.objects.filter(username=username).exists():
                    messages.error(request, "계정이 존재하지 않습니다. 회원가입을 진행해 주세요.")
                else:
                    messages.error(request, "로그인에 실패했습니다. 사용자 이름 또는 비밀번호를 확인하세요.")
        else:
            # 폼 유효성 검증 실패 메시지
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})


# 회원가입을 위한 뷰
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


# 비트코인 가격 변동 데이터를 반환하는 API
@api_view(['GET'])
def btc_forecasting_api(request):
    """
    최근 7일(1440 * 7개)의 비트코인 실제 가격과 예측 가격 데이터를 반환함.
    날짜 필터링(start_date, end_date)도 지원함.
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if start_date and end_date:
        data = Forecast.objects.filter(
            date_time__range=[start_date, end_date]
        ).order_by('-date_time')
    else:
        # 최근 7일치 데이터 가져오기
        data = Forecast.objects.order_by('-date_time')[:1440 * 7]

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


def sentiment_data_api(request, class_id):
    """
    특정 class_id에 대한 감정 분석 데이터를 JSON 형식으로 반환합니다.
    """
    sentiments = Sentiment.objects.filter(class_id=class_id)
    sentiment_counts = sentiments.values('sentiment_value').annotate(count=Count('id'))

    # 결과를 JSON으로 변환
    data = {
        'labels': [item['sentiment_value'] for item in sentiment_counts],
        'counts': [item['count'] for item in sentiment_counts],
    }
    return JsonResponse(data)

