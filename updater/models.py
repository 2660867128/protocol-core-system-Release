"""
更新模块数据模型
"""
from django.db import models
from django.utils import timezone

class UpdateRecord(models.Model):
    """更新记录模型"""
    
    STATUS_CHOICES = [
        ('pending', '等待更新'),
        ('downloading', '下载中'),
        ('downloaded', '下载完成'),
        ('installing', '安装中'),
        ('completed', '更新完成'),
        ('failed', '更新失败'),
        ('rollback', '已回滚'),
    ]
    
    version_from = models.CharField(max_length=50, verbose_name='原版本')
    version_to = models.CharField(max_length=50, verbose_name='目标版本')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    download_url = models.URLField(verbose_name='下载地址')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    downloaded_size = models.BigIntegerField(default=0, verbose_name='已下载大小')
    checksum = models.CharField(max_length=64, blank=True, verbose_name='文件校验值')
    backup_path = models.CharField(max_length=500, blank=True, verbose_name='备份路径')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        verbose_name = '更新记录'
        verbose_name_plural = '更新记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.version_from} -> {self.version_to} ({self.get_status_display()})'
    
    @property
    def progress_percentage(self):
        """下载进度百分比"""
        if self.file_size > 0:
            return min(100, (self.downloaded_size / self.file_size) * 100)
        return 0

class SystemVersion(models.Model):
    """系统版本信息"""
    
    version = models.CharField(max_length=50, unique=True, verbose_name='版本号')
    release_date = models.DateTimeField(verbose_name='发布日期')
    changelog = models.TextField(verbose_name='更新日志')
    download_url = models.URLField(verbose_name='下载地址')
    file_size = models.BigIntegerField(verbose_name='文件大小')
    checksum = models.CharField(max_length=64, verbose_name='文件校验值')
    is_stable = models.BooleanField(default=True, verbose_name='稳定版本')
    min_version = models.CharField(max_length=50, blank=True, verbose_name='最低兼容版本')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '系统版本'
        verbose_name_plural = '系统版本'
        ordering = ['-release_date']
    
    def __str__(self):
        return f'v{self.version} {"(稳定版)" if self.is_stable else "(测试版)"}'
