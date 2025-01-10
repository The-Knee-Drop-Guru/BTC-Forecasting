from decimal import Decimal
from .models import Forecast, TransactionLog
from datetime import timedelta, datetime

def calculate_rsi(prices):
    """
    최근 1시간 데이터만을 사용해 RSI 계산
    """
    if len(prices) < 2:
        print("[RSI] 데이터가 2개 미만으로 계산 불가.")
        return None  # 데이터가 2개 미만이면 계산 불가

    gains = []
    losses = []

    # 최근 1시간 데이터로 상승/하락 계산
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    # print(f"[RSI] 상승 평균: {avg_gain}, 하락 평균: {avg_loss}")

    if avg_loss == 0:
        print("[RSI] 손실이 없으므로 RSI는 100.")
        return 100  # 손실이 없는 경우 RSI는 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    # print(f"[RSI] RS: {rs}, RSI: {rsi}")
    return rsi


def trading_algorithm(current_price, predicted_price, balance, assets, stop_loss, take_profit, prices):
    current_price = Decimal(current_price)
    predicted_price = Decimal(predicted_price)

    action = "HOLD"
    quantity = Decimal(0)
    new_balance = balance
    new_assets = assets 

    stop_loss_price = current_price * (Decimal(1) - Decimal(stop_loss))
    take_profit_price = current_price * (Decimal(1) + Decimal(take_profit))

    # RSI 계산 (최근 가격 리스트 필요)
    rsi = calculate_rsi(prices) if prices else None

    print(f"[Trading] Current Price: {current_price}, Predicted Price: {predicted_price}, RSI: {rsi}")

    # 매수 조건: predicted_price > current_price & RSI 조건
    if predicted_price > current_price and (rsi is None or rsi > 40):
        if balance > 0:  # 잔고가 충분한지 확인
            action = "BUY"
            quantity = (balance * Decimal(0.5)) / current_price  # 잔고의 50%로 매수
            new_balance = balance - (quantity * current_price)
            new_assets = assets + quantity
            print(f"[Trading] 매수: {quantity} @ {current_price}, 잔고: {new_balance}, 자산: {new_assets}")
        else:
            action = "HOLD"
            new_balance = balance
            new_assets = assets
            print(f"[Trading] 잔고 부족으로 매수 불가. 현재 잔고: {balance}")
    # 매도 조건: predicted_price < current_price & RSI 조건
    elif predicted_price < current_price and (rsi is None or rsi < 40) and assets > 0:
        action = "SELL"
        quantity = assets  # 전량 매도
        new_balance = balance + (quantity * current_price)
        new_assets = Decimal(0)
        print(f"[Trading] 매도: {quantity} @ {current_price}, 잔고: {new_balance}, 자산: {new_assets}")
    # 익절 조건: 가격이 목표 이상으로 올라갔을 때
    elif current_price >= take_profit_price and assets > 0:
        action = "TAKE_PROFIT"
        quantity = assets
        new_balance = balance + (quantity * current_price)
        new_assets = Decimal(0)
        print(f"[Trading] 익절: {quantity} @ {current_price}, 잔고: {new_balance}, 자산: {new_assets}")
    # 손절 조건: 가격이 목표 이하로 떨어졌을 때
    elif current_price <= stop_loss_price and assets > 0:
        action = "STOP_LOSS"
        quantity = assets
        new_balance = balance + (quantity * current_price)
        new_assets = Decimal(0)
        print(f"[Trading] 손절: {quantity} @ {current_price}, 잔고: {new_balance}, 자산: {new_assets}")
    else:
        new_balance = balance
        new_assets = assets
        print(f"[Trading] 보유: 잔고 {new_balance}, 자산 {new_assets}")

    total_asset = new_balance + (new_assets * current_price)
    print(f"[Trading] 총자산: {total_asset}")
    return action, quantity, new_balance, new_assets, total_asset



def execute_trading_simulation(user, initial_balance, stop_loss, take_profit):
    """
    지난 1시간의 데이터로 시뮬레이션 실행
    """
    end_time = datetime.now().replace(second=0, microsecond=0)
    print(f"[{end_time}] 사용자 {user.username} 시뮬레이션 시작.")

    # 지난 1시간 동안의 실제 가격 데이터 가져오기
    hourly_forecasts = list(Forecast.objects.filter(
        date_time__lte=end_time,
        real_price__isnull=False
    ).order_by('-date_time')[:60])

    if not hourly_forecasts:
        print(f"[{end_time}] 사용자 {user.username}: 1시간 데이터 부족.")
        raise ValueError("지난 1시간치 데이터가 부족합니다.")
    
    # 시간순으로 재정렬
    hourly_forecasts.sort(key=lambda x: x.date_time)  # `date_time`을 기준으로 오름차순 정렬

    latest_transaction = TransactionLog.objects.filter(user=user).order_by('-timestamp').first()
    if latest_transaction:
        balance = Decimal(latest_transaction.balance)
        assets = Decimal(latest_transaction.asset)
        print(f"[{end_time}] 사용자 {user.username} 이전 거래 기록 로드. 잔고: {balance}, 자산: {assets}")
    else:
        balance = initial_balance
        assets = Decimal("0.00")
        print(f"[{end_time}] 사용자 {user.username} 초기 잔고 설정: {balance}")

    prices = [Decimal(forecast.real_price) for forecast in hourly_forecasts]

    # 다음날 8:59의 예측값 가져오기
    next_day_8_59_kst = datetime.combine(datetime.now().date() + timedelta(days=1), datetime.min.time()) + timedelta(hours=8, minutes=59)
    daily_forecast = Forecast.objects.filter(date_time=next_day_8_59_kst).first()

    if not daily_forecast:
        raise ValueError("다음날 8:59 예측값이 존재하지 않습니다.")
    
    predicted_price = daily_forecast.predicted_price

    transaction_logs = []
    for forecast in hourly_forecasts:
        current_price = Decimal(forecast.real_price)

        action, quantity, balance, assets, total_asset = trading_algorithm(
            current_price=current_price,
            predicted_price=predicted_price,
            balance=balance,
            assets=assets,
            stop_loss=stop_loss,
            take_profit=take_profit,
            prices=prices,
        )

        transaction_logs.append(TransactionLog(
            user=user,
            transaction_type=action,
            quantity=quantity,
            price=current_price,
            amount=quantity * current_price if action != "HOLD" else Decimal("0.00"),
            fee=quantity * current_price * Decimal("0.01") if action != "HOLD" else Decimal("0.00"),
            balance=balance,
            asset=assets,
            timestamp=forecast.date_time
        ))

    if transaction_logs:
        TransactionLog.objects.bulk_create(transaction_logs)
        print(f"[{end_time}] 사용자 {user.username} 거래 로그 저장 완료.")

    last_forecast = hourly_forecasts[-1]
    last_real_price = Decimal(last_forecast.real_price) if last_forecast and last_forecast.real_price else Decimal("0.0")

    result = {
        'final_balance': balance,
        'final_assets': assets,
        'total_asset_value': balance + (assets * last_real_price),
        'total_trades': len([log for log in transaction_logs if log.transaction_type != "HOLD"]),
    }
    print(f"[{end_time}] 사용자 {user.username} 시뮬레이션 완료. 결과: {result}")
    return result