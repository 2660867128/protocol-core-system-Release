@echo off
chcp 65001 >nul
echo 🛑 协议核心管理系统 Docker 停止脚本
echo ========================================

echo.
echo 🔍 检查运行状态...
docker compose ps

echo.
echo 🛑 停止服务...
docker compose down

if %errorlevel% neq 0 (
    echo ❌ 停止服务失败
    pause
    exit /b 1
)

echo.
echo ✅ 服务已停止

echo.
echo 💡 其他操作：
echo    🚀 重新启动: docker compose up -d
echo    📊 查看日志: docker compose logs -f
echo    🗑️ 删除镜像: docker compose down --rmi all
echo    🧹 清理数据: docker compose down -v
echo.
pause
