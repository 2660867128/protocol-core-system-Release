"""
协议配置模型
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from config import PROTOCOL_CONFIG


class ProtocolConfig(models.Model):
    """协议服务配置"""
    
    # 服务配置
    service_password = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name='协议服务密码',
        help_text='设置协议服务API的访问密码，增强安全性'
    )
    
    # 服务端口现在使用 SERVER_CONFIG 中的端口，不再单独设置
    
    # 自动刷新配置
    auto_refresh_enabled = models.BooleanField(
        default=False,
        verbose_name='启用自动刷新',
        help_text='是否启用定时自动刷新微信连接'
    )
    
    refresh_interval = models.IntegerField(
        default=PROTOCOL_CONFIG['DEFAULT_REFRESH_INTERVAL'],
        validators=[
            MinValueValidator(PROTOCOL_CONFIG['MIN_REFRESH_INTERVAL']), 
            MaxValueValidator(PROTOCOL_CONFIG['MAX_REFRESH_INTERVAL'])
        ],
        verbose_name='刷新间隔(分钟)',
        help_text='自动刷新的时间间隔，单位：分钟'
    )
    
    # 刷新配置
    refresh_wechatx_only = models.BooleanField(
        default=PROTOCOL_CONFIG['DEFAULT_REFRESH_WECHATX_ONLY'],
        verbose_name='仅刷新WeChat-X',
        help_text='是否只刷新类型为wechatx的微信连接'
    )
    
    # 自动登录配置
    auto_login_enabled = models.BooleanField(
        default=False,
        verbose_name='启用自动登录',
        help_text='是否启用定时自动登录功能'
    )
    
    auto_login_interval = models.IntegerField(
        default=60,
        validators=[MinValueValidator(5), MaxValueValidator(1440)],
        verbose_name='自动登录间隔(分钟)',
        help_text='自动登录的时间间隔，单位：分钟，范围：5-1440分钟'
    )
    
    # 日志配置
    enable_debug_log = models.BooleanField(
        default=False,
        verbose_name='启用调试日志',
        help_text='是否启用详细的调试日志输出'
    )
    
    log_retention_days = models.IntegerField(
        default=14,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        verbose_name='日志保留天数',
        help_text='自动删除多少天前的日志，范围：1-365天'
    )
    
    # 系统信息
    last_refresh_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='上次刷新时间'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '协议配置'
        verbose_name_plural = '协议配置'
        db_table = 'protocol_config'
    
    def __str__(self):
        from config import SERVER_CONFIG
        return f"协议配置 - 端口:{SERVER_CONFIG['PORT']}"
    
    @classmethod
    def get_config(cls):
        """获取配置实例，如果不存在则创建默认配置"""
        config, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'service_password': '',
                'auto_refresh_enabled': False,
                'refresh_interval': PROTOCOL_CONFIG['DEFAULT_REFRESH_INTERVAL'],
                'refresh_wechatx_only': PROTOCOL_CONFIG['DEFAULT_REFRESH_WECHATX_ONLY'],
                'auto_login_enabled': False,
                'auto_login_interval': 60,
                'enable_debug_log': False,
                'log_retention_days': 14,
            }
        )
        return config


class RefreshLog(models.Model):
    """刷新日志"""
    
    REFRESH_TYPES = [
        ('manual', '手动刷新'),
        ('auto', '自动刷新'),
    ]
    
    refresh_type = models.CharField(
        max_length=10,
        choices=REFRESH_TYPES,
        verbose_name='刷新类型'
    )
    
    connection_count = models.IntegerField(
        default=0,
        verbose_name='刷新连接数'
    )
    
    success_count = models.IntegerField(
        default=0,
        verbose_name='成功数量'
    )
    
    failed_count = models.IntegerField(
        default=0,
        verbose_name='失败数量'
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name='错误信息'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='刷新时间'
    )
    
    class Meta:
        verbose_name = '刷新日志'
        verbose_name_plural = '刷新日志'
        db_table = 'protocol_refresh_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_refresh_type_display()} - {self.success_count}/{self.connection_count}"


class AutoLoginLog(models.Model):
    """自动登录日志"""
    
    LOGIN_TYPES = [
        ('scheduled', '定时任务'),
        ('manual', '手动触发'),
    ]
    
    LOGIN_RESULTS = [
        ('success', '登录成功'),
        ('failed', '登录失败'),
        ('skipped', '跳过（需要二维码）'),
        ('error', '执行错误'),
    ]
    
    login_type = models.CharField(
        max_length=10,
        choices=LOGIN_TYPES,
        verbose_name='登录类型'
    )
    
    wxid = models.CharField(
        max_length=200,
        verbose_name='微信ID'
    )
    
    connection_name = models.CharField(
        max_length=100,
        verbose_name='连接名称'
    )
    
    result = models.CharField(
        max_length=10,
        choices=LOGIN_RESULTS,
        verbose_name='登录结果'
    )
    
    message = models.TextField(
        blank=True,
        verbose_name='详细信息'
    )
    
    response_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name='API响应数据'
    )
    
    duration = models.FloatField(
        null=True,
        blank=True,
        verbose_name='执行时长(秒)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='执行时间'
    )
    
    class Meta:
        verbose_name = '自动登录日志'
        verbose_name_plural = '自动登录日志'
        db_table = 'protocol_auto_login_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wxid} - {self.get_result_display()}"
