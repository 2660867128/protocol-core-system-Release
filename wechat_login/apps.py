"""
微信登录应用配置
"""
from django.apps import AppConfig


class WechatLoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wechat_login'
    verbose_name = '微信登录'
