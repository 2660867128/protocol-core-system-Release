#!/bin/bash

echo "🎯 协议核心管理系统"
echo "================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查是否在项目目录
if [ ! -f "manage.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 运行启动脚本
python3 start.py
