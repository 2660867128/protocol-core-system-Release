"""
在线更新模块应用配置
"""
from django.apps import AppConfig

class UpdaterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'updater'
    verbose_name = '在线更新模块'
