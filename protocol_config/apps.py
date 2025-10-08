from django.apps import AppConfig


class ProtocolConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'protocol_config'
    verbose_name = '协议配置'
    
    def ready(self):
        """应用启动时执行"""
        # 启动自动任务
        try:
            from .models import ProtocolConfig
            from .views import start_auto_refresh_task, start_auto_log_cleanup_task, start_auto_login_task
            
            config = ProtocolConfig.get_config()
            
            # 启动自动刷新任务
            if config.auto_refresh_enabled:
                start_auto_refresh_task()
                print("  自动刷新任务已启动")
            
            # 启动自动登录任务
            if config.auto_login_enabled:
                start_auto_login_task()
                print("  自动登录任务已启动")
            
            # 启动自动日志清理任务
            start_auto_log_cleanup_task()
            print("  自动日志清理任务已启动")
        except Exception as e:
            print(f"  启动自动任务失败: {str(e)}")
