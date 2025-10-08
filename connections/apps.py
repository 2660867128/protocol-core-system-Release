"""
连接管理应用配置
"""
from django.apps import AppConfig


class ConnectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'connections'
    verbose_name = '连接管理'
