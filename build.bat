@echo off
chcp 65001 >nul
echo 🐳 协议核心管理系统 Docker 构建脚本
echo =======================================

echo.
echo 📋 检查Docker环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装或未启动，请先安装Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker环境检查通过

echo.
echo 🔨 构建Docker镜像...
docker compose build

if %errorlevel% neq 0 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)

echo ✅ 镜像构建成功

echo.
echo 🚀 启动服务...
docker compose up -d

if %errorlevel% neq 0 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)

echo.
echo ✅ 服务启动成功！
echo.
echo 📱 访问地址：
echo    🌐 Web界面: http://localhost
echo    🔧 管理后台: http://localhost/admin/
echo    📚 API文档: http://localhost/api/swagger/
echo.
echo 👤 默认账号: admin / admin123456
echo.
echo ⚠️  请在生产环境中修改默认密码！
echo.
echo 📊 查看日志: docker-compose logs -f
echo 🛑 停止服务: docker-compose down
echo.
pause
