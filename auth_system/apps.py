"""
API认证系统应用配置
"""
from django.apps import AppConfig

class AuthSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_system'
    verbose_name = 'API认证系统'
