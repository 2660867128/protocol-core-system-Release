"""
用户认证应用配置
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = '用户管理'
    
    def ready(self):
        """应用启动时执行"""
        import accounts.signals
