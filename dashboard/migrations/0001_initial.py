<<<<<<< HEAD
# Generated by Django 5.1.4 on 2025-01-04 05:32
=======
# Generated by Django 5.1.4 on 2025-01-05 08:38
>>>>>>> develop

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='고유 ID')),
                ('name', models.CharField(max_length=255, verbose_name='피처 이름')),
                ('importance', models.FloatField(verbose_name='피처 중요도')),
                ('date_time', models.DateField(verbose_name='날짜')),
            ],
            options={
                'db_table': 'feature_table',
            },
        ),
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('date_time', models.DateTimeField(primary_key=True, serialize=False, verbose_name='시간')),
                ('real_price', models.FloatField(verbose_name='실제 가격')),
                ('predicted_price', models.FloatField(null=True, verbose_name='예측 가격')),
            ],
            options={
                'db_table': 'forecast_table',
            },
        ),
        migrations.CreateModel(
            name='Sentiment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='고유 ID')),
                ('class_id', models.CharField(choices=[('news', 'news'), ('reddit', 'reddit')], max_length=10, verbose_name='클래스 ID')),
                ('title', models.CharField(max_length=1000, verbose_name='제목')),
                ('sentiment_value', models.CharField(choices=[('positive', 'positive'), ('negative', 'negative'), ('neutral', 'neutral')], max_length=10, verbose_name='감정 분석 결과')),
            ],
            options={
                'db_table': 'sentiment_table',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='사용자 이름')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='이메일')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='이름')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='성')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화 여부')),
                ('is_staff', models.BooleanField(default=False, verbose_name='스태프 여부')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='가입일')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '사용자',
                'verbose_name_plural': '사용자',
                'db_table': 'user_table',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image_url', models.TextField(blank=True, null=True, verbose_name='프로필 이미지 링크')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '사용자 프로필',
                'verbose_name_plural': '사용자 프로필',
                'db_table': 'user_profile_table',
            },
        ),
    ]
