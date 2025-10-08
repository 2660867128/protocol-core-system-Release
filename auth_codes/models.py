"""
授权码管理模型
"""
from django.db import models
from connections.models import AuthCode as BaseAuthCode


# 继承连接应用中的AuthCode模型
# 这里可以添加额外的授权码相关功能

# 为了保持兼容性，重新导出AuthCode
AuthCode = BaseAuthCode
