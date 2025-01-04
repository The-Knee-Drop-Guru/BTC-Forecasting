from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, id, password=None, **extra_fields):
        if not id:
            raise ValueError("사용자 ID는 필수 항목입니다.")
        user = self.model(id=id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(id, password, **extra_fields)

class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=255, unique=True, verbose_name="사용자 ID")
    first_name = models.CharField(max_length=255, verbose_name="이름")
    last_name = models.CharField(max_length=255, verbose_name="성")
    email = models.EmailField(unique=True, verbose_name="이메일")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'user_table'


class UserProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_id', verbose_name="사용자 고유번호")  # FK
    profile_image_url = models.TextField(verbose_name="프로필 이미지 링크")

    class Meta:
        db_table = 'user_profile_table'


# analaytics schema
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

    class Meta:
        db_table = 'feature_table'


class Sentiment(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="고유 ID")
    class_id = models.CharField(max_length=10, choices=[('news', 'news'), ('reddit', 'reddit')], verbose_name="클래스 ID")
    title = models.CharField(max_length=255, verbose_name="제목")
    sentiment_value = models.CharField(max_length=10, choices=[('positive', 'positive'), ('negative', 'negative'), ('neutral', 'neutral')], verbose_name="감정 분석 결과")

    class Meta:
        db_table = 'sentiment_table'