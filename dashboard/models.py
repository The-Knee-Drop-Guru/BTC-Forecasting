from django.db import models

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


# user schema
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, verbose_name="사용자 이름")
    last_name = models.CharField(max_length=255, verbose_name="사용자 성")
    id = models.CharField(max_length=255, unique=True, verbose_name="사용자 ID")
    password = models.CharField(max_length=255, verbose_name="사용자 비밀번호")
    email = models.EmailField(max_length=255, verbose_name="사용자 이메일")

    class Meta:
        db_table = 'user_table'


class UserProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_id', verbose_name="사용자 고유번호")  # FK
    profile_image_url = models.TextField(verbose_name="프로필 이미지 링크")

    class Meta:
        db_table = 'user_profile_table'