from django.apps import AppConfig
import os

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        # 스케줄러 시작
        if os.environ.get('RUN_MAIN', None) != 'true':  # 개발 중 중복 실행 방지
            from .scheduler import start_scheduler
            start_scheduler()