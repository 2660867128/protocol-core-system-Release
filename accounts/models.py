"""
用户模型
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """扩展用户模型"""
    USER_TYPE_CHOICES = [
        ('admin', '管理员'),
        ('user', '普通用户'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='user',
        verbose_name='用户类型'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='手机号'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='头像'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='最后登录IP'
    )
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'auth_user'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_admin(self):
        """是否为管理员"""
        return self.user_type == 'admin' or self.is_superuser
    
    def get_display_name(self):
        """获取显示名称"""
        return self.first_name or self.username


class UserProfile(models.Model):
    """用户配置"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户'
    )
    auto_refresh_interval = models.IntegerField(
        default=120,
        verbose_name='自动刷新间隔(分钟)'
    )
    protocol_password = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='协议服务密码'
    )
    theme = models.CharField(
        max_length=20,
        default='light',
        choices=[
            ('light', '浅色主题'),
            ('dark', '深色主题'),
        ],
        verbose_name='主题'
    )
    
    class Meta:
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'
        db_table = 'user_profile'
    
    def __str__(self):
        return f"{self.user.username}的配置"


class LoginLog(models.Model):
    """登录日志"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_logs',
        verbose_name='用户'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP地址'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='用户代理'
    )
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='登录时间'
    )
    success = models.BooleanField(
        default=True,
        verbose_name='是否成功'
    )
    
    class Meta:
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志'
        db_table = 'login_log'
        ordering = ['-login_time']
    
    def __str__(self):
        status = '成功' if self.success else '失败'
        return f"{self.user.username} - {self.login_time} - {status}"
