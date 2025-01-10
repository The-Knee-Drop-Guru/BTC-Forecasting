from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from decimal import Decimal

# User Manager
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("사용자 이름(username)은 필수 항목입니다.")
        if not email:
            raise ValueError("이메일은 필수 항목입니다.")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, verbose_name="사용자 이름")
    email = models.EmailField(unique=True, verbose_name="이메일")
    first_name = models.CharField(max_length=30, blank=True, verbose_name="이름")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="성")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    is_staff = models.BooleanField(default=False, verbose_name="스태프 여부")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="가입일")

    objects = UserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'user_table'  # user 스키마 지정
        verbose_name = '사용자'
        verbose_name_plural = '사용자'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="사용자")
    profile_image_url = models.TextField(verbose_name="프로필 이미지 링크", blank=True, null=True)

    class Meta:
        db_table = 'user_profile_table'
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필'


class Forecast(models.Model):
    date_time = models.DateTimeField(primary_key=True, verbose_name="시간")
    real_price = models.FloatField(verbose_name="실제 가격")
    predicted_price = models.FloatField(null=True, verbose_name="예측 가격")

    class Meta:
        db_table = 'forecast_table'


class Feature(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="고유 ID")
    name = models.CharField(max_length=255, verbose_name="피처 이름")
    importance = models.FloatField(verbose_name="피처 중요도")
    date_time = models.DateField(verbose_name="날짜")

    class Meta:
        db_table = 'feature_table'


class Sentiment(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="고유 ID")
    class_id = models.CharField(max_length=10, choices=[('news', 'news'), ('reddit', 'reddit')], verbose_name="클래스 ID")
    title = models.CharField(max_length=1000, verbose_name="제목")
    sentiment_value = models.CharField(max_length=10, choices=[('positive', 'positive'), ('negative', 'negative'), ('neutral', 'neutral')], verbose_name="감정 분석 결과")

    class Meta:
        db_table = 'sentiment_table'


# 사용자의 거래 내역
class TransactionLog(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('HOLD', 'Hold'),  # HOLD 추가
    ]
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='user_id', related_name='transaction_logs', verbose_name='사용자')
    timestamp = models.DateTimeField(verbose_name="거래 시간")
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES, verbose_name="거래 유형")
    quantity = models.DecimalField(max_digits=20, decimal_places=8, verbose_name="거래 수량")
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="거래 가격")
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="거래 금액")
    fee = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0.00"), verbose_name="거래 수수료")
    balance = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="잔고")
    asset = models.DecimalField(max_digits=20, decimal_places=8, verbose_name="보유 자산")

    class Meta:
        db_table = 'transaction_log_table'
        verbose_name = '거래 기록'
        verbose_name_plural = '거래 기록'



# 사용자의 일일 최종 거래 내역
class SummaryReport(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='user_id', related_name='summary_reports', verbose_name='사용자')
    date = models.DateField(verbose_name="보고 날짜")
    total_asset_value = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="최종 자산 가치")
    initial_balance = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="최초 자본")
    total_return = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="총 수익률")
    total_trades = models.IntegerField(verbose_name="총 거래 횟수")
    max_loss = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="최대 손실 금액")
    max_profit = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="최대 이익 금액")
    take_profit_count = models.IntegerField(verbose_name="익절 횟수")
    stop_loss_count = models.IntegerField(verbose_name="손절 횟수")

    class Meta:
        db_table = 'summary_report_table'
        verbose_name = '요약 보고서'
        verbose_name_plural = '요약 보고서'