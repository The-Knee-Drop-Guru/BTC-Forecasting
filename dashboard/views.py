from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from .models import Forecast, Feature, User, UserProfile, Sentiment, TransactionLog, SummaryReport
from .forms import SignUpForm
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime, timedelta, time
from .simulation import execute_trading_simulation
from decimal import Decimal

def forecast(request):
    data = Forecast.objects.all()
    response = {
        "time": [entry.date_time.strftime('%Y-%m-%d %H:%M') for entry in data],
        "real_price": [entry.real_price for entry in data],
        "predicted_price": [entry.predicted_price if entry.predicted_price else None for entry in data],
    }
    return JsonResponse(response)

# 대시보드 화면을 위한 뷰
def dashboard(request):
    # 사용자 정보 가져오기
    users = User.objects.all()

    # 사용자 프로필 이미지 URL 가져오기
    user_profiles = UserProfile.objects.all()
    
    # 오늘과 내일 날짜
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # 오늘 오전 8:59의 실제 가격 가져오기
    today_data = Forecast.objects.filter(date_time__date=today, date_time__time=time(8, 59)).first()
    today_price = today_data.real_price if today_data else None

    # 내일 오전 8:59의 예측 가격 가져오기
    tomorrow_data = Forecast.objects.filter(date_time__date=tomorrow, date_time__time=time(8, 59)).first()
    tomorrow_price = tomorrow_data.predicted_price if tomorrow_data else None

    # 메시지 초기화
    if today_price is not None and tomorrow_price is not None:
        # 상승/하락 퍼센트 계산
        percentage_change = ((tomorrow_price - today_price) / today_price) * 100

        if percentage_change > 0:
            forecast_message = f"익일 비트코인 가격은 금일 대비 약 {percentage_change:.2f}% 상승할 것으로 예상됩니다. (UTC 기준)"
        elif percentage_change < 0:
            forecast_message = f"익일 비트코인 가격은 금일 대비 약 {abs(percentage_change):.2f}% 하락할 것으로 예상됩니다. (UTC 기준)"
        else:
            forecast_message = "익일 비트코인 가격은 금일 대비 변동이 없을 것으로 예상됩니다."
    else:
        # 필요한 데이터가 없을 때 처리
        forecast_message = "익일 비트코인 예측 가격이 업데이트 되지 않았습니다."

    # 템플릿에 데이터를 전달
    context = {
        'users': users,
        'user_profiles': user_profiles,
        'date': datetime.now().strftime('%Y-%m-%d'),  # 현재 날짜 추가
        'forecast_message': forecast_message,
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
    선택된 날짜 범위에 따라 비트코인 실제 가격과 예측 가격 데이터를 반환
    날짜가 지정되지 않으면 최신 데이터 기준으로 최근 7일 데이터를 반환
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    # start_date와 end_date가 null 또는 비어 있는 경우 기본값 설정
    if not start_date or start_date == "null":
        try:
            latest_date = Forecast.objects.latest('date_time').date_time
            start_date = (latest_date - timedelta(days=6)).strftime('%Y-%m-%d')
        except Forecast.DoesNotExist:
            return Response({"time": [], "real_price": [], "predicted_price": [], "default_start_date": None, "default_end_date": None})
    
    if not end_date or end_date == "null":
        try:
            latest_date = Forecast.objects.latest('date_time').date_time
            end_date = latest_date.strftime('%Y-%m-%d')
        except Forecast.DoesNotExist:
            return Response({"time": [], "real_price": [], "predicted_price": [], "default_start_date": None, "default_end_date": None})

    # 종료 날짜를 23:59:59로 설정
    end_date_with_time = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    end_date_with_time -= timedelta(seconds=1)

    # 데이터 필터링
    data = Forecast.objects.filter(
        date_time__range=[start_date, end_date_with_time]
    ).order_by('date_time')

    response = {
        "time": [entry.date_time.strftime('%Y-%m-%d %H:%M') for entry in data],
        "real_price": [entry.real_price for entry in data],
        "predicted_price": [entry.predicted_price for entry in data],
        "default_start_date": start_date,  # 기본 시작 날짜
        "default_end_date": end_date,      # 기본 종료 날짜
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
    features = Feature.objects.filter(date_time=latest_date).order_by('-importance')[:5]
    
    # JSON 데이터로 변환
    response_data = {
        "features": [
            {
                "name": feature.name, 
                "importance": round(feature.importance * 100, 1) 
            }
            for feature in features
        ]
    }
    return Response(response_data)


# 에러 데이터를 반환하는 API
@api_view(['GET'])
def error_data_api(request):
    """
    매일 8:59의 실제 값과 예측 값의 오차 데이터를 반환하는 API
    """
    # 8:59 데이터를 필터링
    forecasts = Forecast.objects.filter(date_time__time=time(8, 59)).order_by('date_time')

    # 오차 데이터 계산 및 JSON 변환
    response_data = [
        {
            "date": forecast.date_time.strftime('%Y-%m-%d'),
            "error": forecast.predicted_price - forecast.real_price
        }
        for forecast in forecasts if forecast.predicted_price is not None and forecast.real_price is not None
    ]

    return Response(response_data)


def sentiment_data_api(request, class_id):
    """
    특정 class_id에 대한 감정 분석 데이터를 JSON 형식으로 반환합니다.
    """
    # 감정 분석 데이터 가져오기
    sentiments = Sentiment.objects.filter(class_id=class_id)
    sentiment_counts = sentiments.values('sentiment_value').annotate(count=Count('id'))

    # 결과를 JSON으로 변환
    data = {
        'labels': [item['sentiment_value'] for item in sentiment_counts],
        'counts': [item['count'] for item in sentiment_counts],
    }
    return JsonResponse(data)


# ------------ 모의 트레이딩 ---------------

def set_user_trading_settings(request):
    """
    사용자로부터 초기 트레이딩 설정 값을 입력받아 세션에 저장 후 리다이렉트
    """
    if request.method != 'POST':
        return redirect('dashboard:simulation')

    # 데이터 가져오기
    initial_balance = request.POST.get('initial_balance')
    stop_loss = request.POST.get('max_loss')
    take_profit = request.POST.get('take_profit')

    # 값 확인
    if not all([initial_balance, stop_loss, take_profit]):
        return redirect('dashboard:simulation_view')

    try:
        # 숫자값 유효성 검사
        initial_balance = Decimal(initial_balance)
        stop_loss = Decimal(stop_loss)
        take_profit = Decimal(take_profit)
        if not (0 < stop_loss < 1) or not (0 < take_profit < 1):
            raise ValueError("손절 비율과 익절 비율은 0과 1 사이여야 합니다.")
    except (ValueError, TypeError) as e:
        print(f"유효성 검사 실패: {str(e)}")
        return redirect('dashboard:simulation_view')

    # 세션에 저장
    trading_settings = {
        'initial_balance': str(initial_balance),
        'stop_loss': str(stop_loss),
        'take_profit': str(take_profit),
    }
    request.session['trading_settings'] = trading_settings
    request.session.set_expiry(86400)  # 세션 1일 유지

    print("저장된 세션 데이터:", request.session.get('trading_settings'))

    # 설정 후 재렌더링을 위해 리다이렉트
    return redirect('dashboard:simulation_view')


def process_hourly_data(request):
    """
    지난 1시간치 데이터를 처리하고 시뮬레이션 실행
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST 요청만 허용됩니다.'}, status=400)

    user = request.user
    trading_settings = request.session.get('trading_settings')

    if not trading_settings:
        return JsonResponse({'status': 'error', 'message': '트레이딩 설정이 없습니다. 먼저 설정을 저장하세요.'}, status=400)

    initial_balance = Decimal(trading_settings['initial_balance'])
    stop_loss = Decimal(trading_settings['stop_loss'])
    take_profit = Decimal(trading_settings['take_profit'])

    # 오늘의 예측 가격 가져오기
    today = datetime.now().date()
    daily_forecast = Forecast.objects.filter(date_time__date=today).first()

    if not daily_forecast or not daily_forecast.predicted_price:
        return JsonResponse({'status': 'error', 'message': '오늘의 예측 가격 데이터가 없습니다.'}, status=400)

    daily_predicted_price = Decimal(daily_forecast.predicted_price)

    # 시뮬레이션 실행
    try:
        result = execute_trading_simulation(
            user=user,
            initial_balance=initial_balance,
            stop_loss=stop_loss,
            take_profit=take_profit,
            daily_predicted_price=Decimal(daily_predicted_price),
        )
        return JsonResponse({'status': 'success', 'result': result})
    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def get_transaction_logs(request):
    """
    DB에서 저장된 거래 기록을 불러와 반환
    """
    user = request.user
    logs = TransactionLog.objects.filter(user=user).order_by('-timestamp')

    # 로그 데이터 직렬화
    transaction_data = [
        {
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_type": log.transaction_type,
            "quantity": float(log.quantity),
            "price": float(log.price),
            "amount": float(log.amount),
            "fee": float(log.fee),
            "balance": float(log.balance),
            "asset": float(log.asset),
        }
        for log in logs
    ]

    return JsonResponse({"status": "success", "transactions": transaction_data})

def check_simulation_status(request):
    """
    시뮬레이션 상태를 확인하고 반환
    """
    user = request.user

    # 세션에서 시뮬레이션 설정과 상태 가져오기
    simulation_settings = request.session.get('trading_settings')
    simulation_status = request.session.get('simulation_status', 'idle')  # 기본값: idle

    if not simulation_settings:
        return JsonResponse({'status': 'error', 'message': '트레이딩 설정이 없습니다.'})

    try:
        # 세션 만료 시간 확인 및 상태 업데이트
        if request.session.get_expiry_age() <= 0:
            simulation_status = 'completed'
        else:
            simulation_status = 'running'
        request.session['simulation_status'] = simulation_status
        request.session.modified = True  # 세션 강제 저장
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'상태 확인 중 오류 발생: {str(e)}'})

    return JsonResponse({'status': simulation_status})

def simulation_view(request):
    """
    시뮬레이션 페이지 렌더링
    """
    user = request.user

    # 세션 값 가져오기
    trading_settings = request.session.get('trading_settings')
    if not trading_settings:
        return render(request, 'dashboard/simulation.html', {
            'error': '트레이딩 설정이 없습니다. 먼저 설정을 저장하세요.',
            'logs': [],
            'summary': None,
            'result': None,
        })

    # 저장된 거래 로그 가져오기
    logs = TransactionLog.objects.filter(user=user).order_by('-timestamp')

    # 거래 요약 정보 가져오기
    summary = SummaryReport.objects.filter(user=user).order_by('-date').first()

    # 최종 요약 데이터 생성
    if logs.exists():
        final_log = logs.first()
        result = {
            "final_balance": final_log.balance,
            "final_assets": final_log.asset,
            "total_asset_value": final_log.balance + (final_log.asset * final_log.price if final_log.price else 0),
            "total_trades": logs.count(),
        }
        
        # 초기 자산과 최종 자산을 비교하여 수익률 계산
        initial_asset_value = Decimal(trading_settings['initial_balance'])
        final_asset_value = result["total_asset_value"]
        total_return = ((final_asset_value - initial_asset_value) / initial_asset_value) * 100  # 수익률 계산
        result['total_return'] = total_return
    else:
        initial_balance = Decimal(trading_settings['initial_balance'])
        result = {
            "final_balance": initial_balance, 
            "final_assets": Decimal(0),
            "total_asset_value": initial_balance,
            "total_trades": 0,
            "total_return": 0, 
        }

    context = {
        'logs': logs,
        'summary': summary,
        'current_balance': result['final_balance'] if result else 0, 
        'current_asset': result['final_assets'] if result else 0, 
        'result': result,
    }

    return render(request, 'dashboard/simulation.html', context)
