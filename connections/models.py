"""
连接管理模型
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
import json

User = get_user_model()


class Connection(models.Model):
    """连接配置"""
    CONNECTION_TYPES = [
        ('WeCharPadPro', 'WeCharPadPro'),
        ('wechatx', 'wechatx'),
        ('wechatx-861', 'wechatx-861'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='connections',
        verbose_name='用户'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='连接名称'
    )
    url = models.URLField(
        verbose_name='接口地址',
        validators=[URLValidator()]
    )
    connection_type = models.CharField(
        max_length=20,
        choices=CONNECTION_TYPES,
        default='WeCharPadPro',
        verbose_name='连接类型'
    )
    admin_key = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='管理员密钥'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
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
        verbose_name = '连接配置'
        verbose_name_plural = '连接配置'
        db_table = 'connection'
        unique_together = ['user', 'name']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.connection_type}] {self.name} - {self.user.username}"
    
    @property
    def display_name(self):
        """显示名称"""
        return f"[{self.connection_type}] {self.name} [{self.url}]"
    
    def test_connection(self):
        """测试连接"""
        import requests
        try:
            # 根据连接类型选择不同的测试端点
            if self.connection_type == 'WeCharPadPro':
                # 测试WeCharPadPro的健康检查端点
                test_url = f"{self.url.rstrip('/')}/health"
                response = requests.get(test_url, timeout=5)
                return response.status_code == 200
            elif self.connection_type in ['wechatx', 'wechatx-861']:
                # 测试wechatx类型的API端点
                test_url = f"{self.url.rstrip('/')}/api/Login/GetQR"
                headers = {"accept": "application/json", "Content-Type": "application/json"}
                response = requests.post(test_url, headers=headers, json={}, timeout=5)
                # 即使返回错误，只要能连接到服务器就算成功
                return response.status_code in [200, 400, 401, 403, 500]
            else:
                # 默认测试：尝试访问根路径
                response = requests.get(f"{self.url.rstrip('/')}/", timeout=5)
                return response.status_code < 500
        except requests.exceptions.ConnectTimeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            # 其他异常也认为连接失败
            return False


class AuthCode(models.Model):
    """授权码"""
    connection = models.ForeignKey(
        Connection,
        on_delete=models.CASCADE,
        related_name='auth_codes',
        verbose_name='连接'
    )
    code = models.CharField(
        max_length=200,
        verbose_name='授权码/WXID'
    )
    remark = models.TextField(
        blank=True,
        default='',
        verbose_name='备注'
    )
    avatar_url = models.URLField(
        blank=True,
        default='',
        verbose_name='头像链接'
    )
    nickname = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='微信昵称'
    )
    last_query_success = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='最后查询是否成功'
    )
    last_query_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后查询时间'
    )
    is_online = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='是否在线'
    )
    last_status_check_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后状态检查时间'
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
        verbose_name = '授权码'
        verbose_name_plural = '授权码'
        db_table = 'auth_code'
        unique_together = ['connection', 'code']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.connection.name}"
    
    @property
    def remark_list(self):
        """获取备注列表"""
        if not self.remark:
            return []
        try:
            # 尝试解析JSON格式的备注
            result = json.loads(self.remark)
            # 确保返回的是列表
            if isinstance(result, list):
                return result
            elif isinstance(result, str):
                return [result]
            else:
                return [str(result)]
        except:
            # 如果不是JSON，按逗号分割
            if isinstance(self.remark, str):
                return [r.strip() for r in self.remark.split(',') if r.strip()]
            else:
                return [str(self.remark)]
    
    @remark_list.setter
    def remark_list(self, value):
        """设置备注列表"""
        if isinstance(value, list):
            self.remark = json.dumps(value, ensure_ascii=False)
        else:
            self.remark = str(value)
    
    @property
    def remark_display(self):
        """显示用的备注"""
        try:
            remarks = self.remark_list
            if remarks and isinstance(remarks, (list, tuple)):
                return ', '.join(str(r) for r in remarks)
            elif remarks and isinstance(remarks, str):
                return remarks
            elif self.remark:
                return str(self.remark)
            return self.code
        except Exception:
            # 如果出现任何错误，返回原始备注或代码
            return str(self.remark) if self.remark else self.code
    
    @property
    def status_display(self):
        """状态显示"""
        if self.is_online is None:
            return '未知'
        elif self.is_online:
            return '在线'
        else:
            return '离线'
    
    @property
    def status_class(self):
        """状态CSS类"""
        if self.is_online is None:
            return 'secondary'
        elif self.is_online:
            return 'success'
        else:
            return 'danger'


class ConnectionLog(models.Model):
    """连接日志"""
    LOG_TYPES = [
        ('login', '登录'),
        ('query', '查询'),
        ('generate', '生成授权码'),
        ('error', '错误'),
    ]
    
    connection = models.ForeignKey(
        Connection,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='连接'
    )
    log_type = models.CharField(
        max_length=20,
        choices=LOG_TYPES,
        verbose_name='日志类型'
    )
    message = models.TextField(
        verbose_name='日志消息'
    )
    success = models.BooleanField(
        default=True,
        verbose_name='是否成功'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '连接日志'
        verbose_name_plural = '连接日志'
        db_table = 'connection_log'
        ordering = ['-created_at']
    
    def __str__(self):
        status = '成功' if self.success else '失败'
        return f"{self.connection.name} - {self.get_log_type_display()} - {status}"


class ChatMessage(models.Model):
    """聊天消息记录"""
    auth_code = models.ForeignKey(
        AuthCode,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='授权码'
    )
    message_id = models.CharField(
        max_length=100,
        verbose_name='消息ID',
        help_text='协议返回的NewMsgId'
    )
    from_user = models.CharField(
        max_length=100,
        verbose_name='发送者',
        help_text='FromUserName'
    )
    to_user = models.CharField(
        max_length=100,
        verbose_name='接收者',
        help_text='ToUserName'
    )
    content = models.TextField(
        verbose_name='消息内容'
    )
    push_content = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='推送内容',
        help_text='发送者昵称等'
    )
    message_type = models.CharField(
        max_length=20,
        default='text',
        verbose_name='消息类型',
        help_text='text, image, file等'
    )
    is_from_self = models.BooleanField(
        default=False,
        verbose_name='是否为自己发送'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        db_table = 'chat_message'
        unique_together = ['auth_code', 'message_id']
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['auth_code', 'created_at']),
            models.Index(fields=['from_user', 'to_user']),
        ]
    
    def __str__(self):
        return f"{self.from_user} -> {self.to_user}: {self.content[:50]}"
    
    @property
    def chat_partner(self):
        """获取聊天对象"""
        if self.is_from_self:
            return self.to_user
        else:
            return self.from_user
    
    @property
    def display_name(self):
        """显示名称"""
        if self.is_from_self:
            return '我'
        else:
            return self.push_content or self.from_user


class ChatSession(models.Model):
    """聊天会话"""
    auth_code = models.ForeignKey(
        AuthCode,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name='授权码'
    )
    partner_id = models.CharField(
        max_length=100,
        verbose_name='聊天对象ID'
    )
    partner_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='聊天对象名称'
    )
    last_message = models.ForeignKey(
        ChatMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='最后一条消息'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name='最后活动时间'
    )
    unread_count = models.IntegerField(
        default=0,
        verbose_name='未读消息数'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'
        db_table = 'chat_session'
        unique_together = ['auth_code', 'partner_id']
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['auth_code', 'last_activity']),
        ]
    
    def __str__(self):
        return f"{self.auth_code.code} - {self.partner_name or self.partner_id}"
