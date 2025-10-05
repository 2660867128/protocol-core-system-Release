#!/bin/bash

# 协议核心管理系统 Docker 启动脚本

set -e

echo "🚀 启动协议核心管理系统..."

# 设置Python路径
export PYTHONPATH=/app:$PYTHONPATH
cd /app

# 等待数据库准备就绪
echo "📊 准备数据库..."
python manage.py migrate --noinput

# 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput

# 创建超级用户（如果不存在）
echo "👤 创建超级用户..."
python docker/create_superuser.py

# 创建必要的目录
mkdir -p /app/data /app/media /app/logs /var/log/nginx /var/log/supervisor

# 设置权限
chown -R appuser:appuser /app/data /app/media /app/logs
chown -R www-data:www-data /var/log/nginx

echo "✅ 初始化完成！"
echo "🌐 Web界面: http://localhost"
echo "🔧 管理后台: http://localhost/admin/"
echo "📚 API文档: http://localhost/api/swagger/"
echo "👤 默认账号: admin / admin"
echo ""
echo "⚠️  请在生产环境中修改默认密码和SECRET_KEY！"

# 启动 supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
