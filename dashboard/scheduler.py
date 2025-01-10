from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, time
from decimal import Decimal
from django.contrib.sessions.models import Session
from .models import User
from dashboard.simulation import execute_trading_simulation


def scheduled_task():
    """
    매 시간마다 실행될 작업
    """
    now = datetime.now()
    print(f"[{now}] 자동 매매 작업 시작")

    try:
        # 활성 사용자 세션 가져오기
        active_sessions = Session.objects.filter(expire_date__gte=now)
        print(f"[{now}] 활성 세션 수: {active_sessions.count()}")

        for session in active_sessions:
            try:
                session_data = session.get_decoded()

                # 세션에서 필요한 데이터 확인
                if 'trading_settings' not in session_data or '_auth_user_id' not in session_data:
                    print(f"[{now}] 세션 {session.session_key}에 필요한 데이터 없음. 건너뜀.")
                    continue

                user_id = session_data['_auth_user_id']
                trading_settings = session_data['trading_settings']

                # 사용자 데이터 로드
                user = User.objects.get(user_id=user_id)
                initial_balance = Decimal(trading_settings['initial_balance'])
                stop_loss = Decimal(trading_settings['stop_loss'])
                take_profit = Decimal(trading_settings['take_profit'])
                print(f"[{now}] 사용자 {user.username} 데이터 로드 완료.")

                # 매매 실행
                result = execute_trading_simulation(
                    user=user,
                    initial_balance=initial_balance,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                )
                print(f"[{now}] 사용자 {user.username} 거래 완료. 결과: {result}")
            except Exception as e:
                print(f"[{now}] 사용자 ID {user_id} 처리 중 오류: {str(e)}")
    except Exception as e:
        print(f"[{now}] 스케줄링 작업 중 예외 발생: {str(e)}")

    print(f"[{now}] 자동 매매 작업 완료")


def start_scheduler():
    """
    스케줄러를 시작
    """
    try:
        scheduler = BackgroundScheduler()
        trigger = CronTrigger(minute=11)
        scheduler.add_job(scheduled_task, trigger)
        scheduler.start()
        print(f"[{datetime.now()}] 스케줄러가 시작되었습니다.")
    except Exception as e:
        print(f"[{datetime.now()}] 스케줄러 시작 중 예외 발생: {str(e)}")
