"""
阅读过检配置模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ReadCheckConfig(models.Model):
    """阅读过检配置"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='read_check_configs',
        verbose_name='用户'
    )
    protocol_url = models.URLField(
        verbose_name='协议地址'
    )
    wxids = models.JSONField(
        default=list,
        verbose_name='微信ID列表'
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
    
    # 统计字段
    total_checks = models.IntegerField(
        default=0,
        verbose_name='总检测次数'
    )
    success_checks = models.IntegerField(
        default=0,
        verbose_name='成功检测次数'
    )
    failed_checks = models.IntegerField(
        default=0,
        verbose_name='失败检测次数'
    )
    
    class Meta:
        verbose_name = '阅读过检配置'
        verbose_name_plural = '阅读过检配置'
        db_table = 'read_check_config'
        unique_together = ['user', 'protocol_url']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.protocol_url}"
    
    @property
    def wxid_count(self):
        """微信ID数量"""
        return len(self.wxids) if self.wxids else 0
    
    @property
    def success_rate(self):
        """成功率"""
        if self.total_checks == 0:
            return 0
        return round((self.success_checks / self.total_checks) * 100, 2)
    
    def increment_check_count(self, success=True):
        """增加检测次数"""
        self.total_checks += 1
        if success:
            self.success_checks += 1
        else:
            self.failed_checks += 1
        self.save(update_fields=['total_checks', 'success_checks', 'failed_checks'])


class ReadCheckLog(models.Model):
    """阅读过检日志"""
    config = models.ForeignKey(
        ReadCheckConfig,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='配置'
    )
    url = models.URLField(
        verbose_name='检查的URL'
    )
    wxid = models.CharField(
        max_length=100,
        verbose_name='微信ID'
    )
    read_count_before = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='检查前阅读量'
    )
    read_count_after = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='检查后阅读量'
    )
    increased = models.BooleanField(
        default=False,
        verbose_name='是否增加'
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
        verbose_name='检查时间'
    )
    
    class Meta:
        verbose_name = '阅读过检日志'
        verbose_name_plural = '阅读过检日志'
        db_table = 'read_check_log'
        ordering = ['-created_at']
    
    def __str__(self):
        status = '成功' if self.success else '失败'
        return f"{self.wxid} - {status} - {self.created_at}"


class ReadCheckSession(models.Model):
    """阅读链接检测会话"""
    STATUS_CHOICES = [
        ('running', '检测中'),
        ('completed', '已完成'),
        ('failed', '检测失败'),
    ]
    
    RESULT_CHOICES = [
        ('increased', '发现阅读量变化'),
        ('no_change', '未发现阅读量变化'),
        ('error', '检测出错'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    url = models.URLField(verbose_name="检测链接")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running', verbose_name="状态")
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, null=True, blank=True, verbose_name="检测结果")
    
    # 统计信息
    total_accounts = models.IntegerField(default=0, verbose_name="总账号数")
    successful_accounts = models.IntegerField(default=0, verbose_name="成功检测账号数")
    failed_accounts = models.IntegerField(default=0, verbose_name="失败账号数")
    
    # 阅读量变化信息
    initial_read_count = models.IntegerField(null=True, blank=True, verbose_name="初始阅读量")
    final_read_count = models.IntegerField(null=True, blank=True, verbose_name="最终阅读量")
    increased_count = models.IntegerField(default=0, verbose_name="增加的阅读量")
    
    # 时间信息
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    
    class Meta:
        verbose_name = "阅读检测会话"
        verbose_name_plural = "阅读检测会话"
        db_table = 'read_check_session'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.url[:50]} - {self.get_status_display()} - {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @property
    def duration(self):
        """检测持续时间"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def duration_seconds(self):
        """检测持续时间（秒）"""
        duration = self.duration
        return duration.total_seconds() if duration else None


class ReadCheckProcessLog(models.Model):
    """阅读检测流程日志"""
    LOG_TYPE_CHOICES = [
        ('start', '开始检测'),
        ('target_url', '目标文章'),
        ('protocol', '使用协议'),
        ('account', '检测账号'),
        ('first_read', '第一次阅读量'),
        ('second_read', '第二次阅读量'),
        ('read_change', '阅读量变化'),
        ('warning', '警告'),
        ('error', '错误'),
        ('complete', '检测完成'),
    ]
    
    session = models.ForeignKey(ReadCheckSession, on_delete=models.CASCADE, related_name='process_logs', verbose_name="检测会话")
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES, verbose_name="日志类型")
    message = models.TextField(verbose_name="日志消息")
    
    # 账号相关信息
    wxid = models.CharField(max_length=100, blank=True, verbose_name="微信ID")
    protocol_url = models.URLField(blank=True, verbose_name="协议地址")
    
    # 阅读量信息
    read_count = models.IntegerField(null=True, blank=True, verbose_name="阅读量")
    previous_read_count = models.IntegerField(null=True, blank=True, verbose_name="之前阅读量")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "检测流程日志"
        verbose_name_plural = "检测流程日志"
        db_table = 'read_check_process_log'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.session.id} - {self.get_log_type_display()} - {self.created_at.strftime('%H:%M:%S')}"
    
    @property
    def formatted_time(self):
        """格式化时间"""
        return self.created_at.strftime('[%H:%M:%S]')
    
    @property
    def icon(self):
        """获取日志类型对应的图标"""
        icons = {
            'start': '🚀',
            'target_url': '🔗',
            'protocol': '📡',
            'account': '👤',
            'first_read': '📊',
            'second_read': '📊',
            'read_change': '🎉',
            'warning': '⚠️',
            'error': '❌',
            'complete': '✅',
        }
        return icons.get(self.log_type, '📝')
