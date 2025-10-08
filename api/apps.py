"""
API应用配置
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'RESTful API'
    
    def ready(self):
        """应用准备就绪时的初始化操作"""
        pass
