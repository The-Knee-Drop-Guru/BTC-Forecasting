from django.shortcuts import render
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

