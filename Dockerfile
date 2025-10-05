# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=protocol_core.settings
ENV DEBUG=False
ENV PYTHONPATH=/app:$PYTHONPATH
ENV DOCKER_CONTAINER=true

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/staticfiles /app/media /app/data /app/logs

# 设置启动脚本权限
RUN chmod +x /app/start.py

# 创建非root用户并设置权限
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# 暴露端口
EXPOSE 8000

# 切换到非root用户
USER appuser

# 启动命令 - 使用start.py作为启动脚本
CMD ["python", "/app/start.py"]
