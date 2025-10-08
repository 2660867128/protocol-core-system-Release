"""
协议服务API应用配置
"""
from django.apps import AppConfig


class ProtocolApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'protocol_api'
    verbose_name = '协议服务API'
