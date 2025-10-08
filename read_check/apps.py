"""
阅读过检应用配置
"""
from django.apps import AppConfig


class ReadCheckConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'read_check'
    verbose_name = '阅读过检'
