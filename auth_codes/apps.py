"""
授权码管理应用配置
"""
from django.apps import AppConfig


class AuthCodesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_codes'
    verbose_name = '授权码管理'
