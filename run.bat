@echo off
chcp 65001 >nul
echo 🎯 协议核心管理系统
echo ================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查是否在项目目录
if not exist "manage.py" (
    echo ❌ 错误：请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 运行启动脚本
python start.py

pause
