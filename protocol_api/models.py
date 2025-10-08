"""
协议服务API模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class APIRequest(models.Model):
    """API请求记录"""
    REQUEST_TYPES = [
        ('get_code', '获取Code'),
        ('get_all_wxids', '获取所有WXID'),
        ('read_article', '阅读文章'),
        ('get_mobile', '获取手机号'),
        ('get_openid', '获取OpenID'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_requests',
        verbose_name='用户'
    )
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPES,
        verbose_name='请求类型'
    )
    wxid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='微信ID'
    )
    appid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='应用ID'
    )
    request_data = models.JSONField(
        default=dict,
        verbose_name='请求数据'
    )
    response_data = models.JSONField(
        default=dict,
        verbose_name='响应数据'
    )
    success = models.BooleanField(
        default=True,
        verbose_name='是否成功'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='错误信息'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP地址'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='用户代理'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='请求时间'
    )
    
    class Meta:
        verbose_name = 'API请求记录'
        verbose_name_plural = 'API请求记录'
        db_table = 'api_request'
        ordering = ['-created_at']
    
    def __str__(self):
        status = '成功' if self.success else '失败'
        return f"{self.get_request_type_display()} - {self.wxid} - {status}"


class APIKey(models.Model):
    """API密钥"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys',
        verbose_name='用户'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='密钥名称'
    )
    key = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='密钥'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    permissions = models.JSONField(
        default=list,
        verbose_name='权限列表'
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后使用时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = 'API密钥'
        verbose_name_plural = 'API密钥'
        db_table = 'api_key'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def has_permission(self, permission):
        """检查是否有指定权限"""
        return permission in self.permissions or 'all' in self.permissions
