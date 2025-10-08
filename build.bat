@echo off
chcp 65001 >nul
title 协议核心管理系统 - Docker 镜像构建工具

echo.
echo ================================================
echo   协议核心管理系统 - Docker 镜像构建工具
echo ================================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装或未启动
    echo 请先安装 Docker Desktop 并确保服务正在运行
    pause
    exit /b 1
)

echo ✅ Docker 环境检查通过
echo.

REM 检查 Dockerfile 文件
if not exist "Dockerfile" (
    echo ❌ 未找到 Dockerfile 文件
    echo 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

echo ✅ Dockerfile 文件检查通过
echo.

REM 设置默认镜像名称
set DEFAULT_IMAGE_NAME=protocol-core-system
set DEFAULT_TAG=latest

echo 🏷️  镜像标签设置
echo ================================================
echo.
echo 默认镜像名称: %DEFAULT_IMAGE_NAME%
echo 默认标签: %DEFAULT_TAG%
echo.
echo 💡 标签命名建议:
echo    - latest: 最新版本
echo    - v1.0.0: 版本号标签
echo    - dev: 开发版本
echo    - prod: 生产版本
echo    - 20241006: 日期标签
echo.

REM 询问用户是否使用自定义标签
set /p USE_CUSTOM_TAG="是否使用自定义标签？(y/N): "
if /i "%USE_CUSTOM_TAG%"=="y" (
    set /p CUSTOM_TAG="请输入自定义标签: "
    if "!CUSTOM_TAG!"=="" (
        echo ⚠️  标签不能为空，使用默认标签: %DEFAULT_TAG%
        set IMAGE_TAG=%DEFAULT_TAG%
    ) else (
        set IMAGE_TAG=!CUSTOM_TAG!
    )
) else (
    set IMAGE_TAG=%DEFAULT_TAG%
)

set FULL_IMAGE_NAME=%DEFAULT_IMAGE_NAME%:%IMAGE_TAG%

echo.
echo 🔧 构建配置信息
echo ================================================
echo 镜像名称: %FULL_IMAGE_NAME%
echo 构建时间: %date% %time%
echo.

REM 确认构建
set /p CONFIRM_BUILD="确认开始构建镜像？(Y/n): "
if /i "%CONFIRM_BUILD%"=="n" (
    echo ❌ 用户取消构建
    pause
    exit /b 0
)

echo.
echo 🚀 开始构建 Docker 镜像...
echo ================================================
echo.

REM 显示构建上下文信息
echo 🔍 构建上下文检查:
echo    当前目录: %CD%
echo    Dockerfile: 
if exist "Dockerfile" (echo    ✅ 存在) else (echo    ❌ 不存在)
echo    requirements.txt: 
if exist "requirements.txt" (echo    ✅ 存在) else (echo    ❌ 不存在)
echo.

REM 构建 Docker 镜像
echo 📦 执行构建命令: docker build -t %FULL_IMAGE_NAME% .
docker build -t %FULL_IMAGE_NAME% .

if %errorlevel% neq 0 (
    echo.
    echo ❌ 镜像构建失败！
    echo 请检查 Dockerfile 和构建日志
    pause
    exit /b 1
)

echo.
echo ✅ 镜像构建成功！
echo.
echo 📦 构建完成信息
echo ================================================
echo 镜像名称: %FULL_IMAGE_NAME%
echo 镜像大小: 
docker images %DEFAULT_IMAGE_NAME% --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | findstr %IMAGE_TAG%
echo.

REM 询问是否推送到 Docker 仓库
echo 🚀 Docker 仓库推送
echo ================================================
echo.
echo 💡 推送选项:
echo    1. 跳过推送（仅本地构建）
echo    2. 推送到 Docker Hub
echo    3. 推送到私有仓库
echo.

set /p PUSH_OPTION="请选择推送选项 (1-3): "

if "%PUSH_OPTION%"=="1" (
    echo ✅ 跳过推送，镜像仅保存在本地
    goto :end
)

if "%PUSH_OPTION%"=="2" (
    echo.
    echo 📤 准备推送到 Docker Hub...
    echo.
    echo ⚠️  请确保已登录 Docker Hub: docker login
    echo.
    set /p DOCKERHUB_USERNAME="请输入 Docker Hub 用户名: "
    if "!DOCKERHUB_USERNAME!"=="" (
        echo ❌ 用户名不能为空
        goto :end
    )
    
    set DOCKERHUB_IMAGE=!DOCKERHUB_USERNAME!/%DEFAULT_IMAGE_NAME%:%IMAGE_TAG%
    
    echo 🏷️  为 Docker Hub 创建标签...
    docker tag %FULL_IMAGE_NAME% !DOCKERHUB_IMAGE!
    
    if !errorlevel! neq 0 (
        echo ❌ 创建标签失败
        goto :end
    )
    
    echo 📤 推送到 Docker Hub...
    docker push !DOCKERHUB_IMAGE!
    
    if !errorlevel! neq 0 (
        echo ❌ 推送失败，请检查网络连接和登录状态
        goto :end
    )
    
    echo ✅ 成功推送到 Docker Hub: !DOCKERHUB_IMAGE!
    goto :end
)

if "%PUSH_OPTION%"=="3" (
    echo.
    echo 📤 准备推送到私有仓库...
    echo.
    set /p PRIVATE_REGISTRY="请输入私有仓库地址 (例: registry.example.com): "
    if "!PRIVATE_REGISTRY!"=="" (
        echo ❌ 仓库地址不能为空
        goto :end
    )
    
    set PRIVATE_IMAGE=!PRIVATE_REGISTRY!/%DEFAULT_IMAGE_NAME%:%IMAGE_TAG%
    
    echo 🏷️  为私有仓库创建标签...
    docker tag %FULL_IMAGE_NAME% !PRIVATE_IMAGE!
    
    if !errorlevel! neq 0 (
        echo ❌ 创建标签失败
        goto :end
    )
    
    echo 📤 推送到私有仓库...
    docker push !PRIVATE_IMAGE!
    
    if !errorlevel! neq 0 (
        echo ❌ 推送失败，请检查网络连接和仓库访问权限
        goto :end
    )
    
    echo ✅ 成功推送到私有仓库: !PRIVATE_IMAGE!
    goto :end
)

echo ❌ 无效的选项，跳过推送

:end
echo.
echo 🎉 构建流程完成！
echo ================================================
echo.
echo 📋 可用命令:
echo    🔍 查看镜像: docker images %DEFAULT_IMAGE_NAME%
echo    🚀 运行容器: docker run -d -p 8000:8000 %FULL_IMAGE_NAME%
echo    🗑️  删除镜像: docker rmi %FULL_IMAGE_NAME%
echo.
echo 💡 提示:
echo    - 使用 docker-compose.yml 可以更方便地管理服务
echo    - 生产环境建议使用具体版本标签而非 latest
echo    - 定期清理不用的镜像: docker image prune
echo.
pause
