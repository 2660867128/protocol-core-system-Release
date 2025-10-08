"""
微信登录模型
"""
from django.db import models
from django.contrib.auth import get_user_model
from connections.models import Connection

User = get_user_model()


class QRCodeSession(models.Model):
    """二维码会话"""
    SESSION_TYPES = [
        ('ipad', 'iPad登录'),
        ('ipad_backup', 'iPad备用登录'),
        ('car', '车载登录'),
        ('861_ipad', '861-iPad登录'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '等待扫码'),
        ('scanned', '已扫码'),
        ('confirmed', '已确认'),
        ('success', '登录成功'),
        ('failed', '登录失败'),
        ('expired', '已过期'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='qr_sessions',
        verbose_name='用户'
    )
    connection = models.ForeignKey(
        Connection,
        on_delete=models.CASCADE,
        related_name='qr_sessions',
        verbose_name='连接'
    )
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPES,
        verbose_name='会话类型'
    )
    uuid = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='会话UUID'
    )
    qr_code_url = models.TextField(
        blank=True,
        verbose_name='二维码URL'
    )
    qr_base64 = models.TextField(
        blank=True,
        verbose_name='二维码Base64'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    wxid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='微信ID'
    )
    nickname = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='昵称'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    expires_at = models.DateTimeField(
        verbose_name='过期时间'
    )
    
    class Meta:
        verbose_name = '二维码会话'
        verbose_name_plural = '二维码会话'
        db_table = 'qr_code_session'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_session_type_display()} - {self.get_status_display()}"
    
    @property
    def is_expired(self):
        """是否已过期"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def update_status(self, status, wxid=None, nickname=None):
        """更新状态"""
        self.status = status
        if wxid:
            self.wxid = wxid
        if nickname:
            self.nickname = nickname
        self.save()


class LoginRecord(models.Model):
    """登录记录"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wechat_login_records',
        verbose_name='用户'
    )
    connection = models.ForeignKey(
        Connection,
        on_delete=models.CASCADE,
        related_name='login_records',
        verbose_name='连接'
    )
    LOGIN_TYPES = [
        ('ipad', 'iPad登录'),
        ('ipad_backup', 'iPad备用登录'),
        ('car', '车载登录'),
        ('861_ipad', '861-iPad登录'),
        ('auto', '自动登录'),
    ]
    
    login_type = models.CharField(
        max_length=20,
        choices=LOGIN_TYPES,
        verbose_name='登录类型'
    )
    wxid = models.CharField(
        max_length=100,
        verbose_name='微信ID'
    )
    nickname = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='昵称'
    )
    success = models.BooleanField(
        default=True,
        verbose_name='是否成功'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='错误信息'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='登录时间'
    )
    
    class Meta:
        verbose_name = '登录记录'
        verbose_name_plural = '登录记录'
        db_table = 'wechat_login_record'
        ordering = ['-created_at']
    
    def __str__(self):
        status = '成功' if self.success else '失败'
        return f"{self.wxid} - {self.get_login_type_display()} - {status}"
