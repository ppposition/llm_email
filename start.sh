#!/bin/bash

# 邮箱管理系统启动脚本

echo "邮箱管理系统启动脚本"
echo "===================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查是否存在.env文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，正在从.env.example复制..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "已创建.env文件，请编辑其中的配置项"
        echo "特别是以下配置项："
        echo "- EMAIL_ADDRESS: 您的邮箱地址"
        echo "- EMAIL_PASSWORD: 您的邮箱密码或应用专用密码"
        echo "- IMAP_SERVER: 您的邮箱IMAP服务器地址"
        echo "- GEMINI_API_KEY: 您的Gemini API密钥"
        echo "- QWEN_API_KEY: 您的Qwen API密钥"
        echo "- LLM_MODEL: 要使用的模型（默认: gemini-2.5-pro）"
        echo ""
        echo "请编辑.env文件后重新运行此脚本"
        exit 1
    else
        echo "错误: 未找到.env.example文件"
        exit 1
    fi
fi

# 检查依赖是否安装
echo "检查依赖..."
if ! python3 -c "import langchain, langchain_openai, flask" &> /dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

# 运行配置测试
echo ""
echo "运行配置测试..."
python3 test_config.py
if [ $? -ne 0 ]; then
    echo ""
    echo "配置测试失败，请检查配置后重试"
    exit 1
fi

echo ""
echo "配置测试通过，正在启动系统..."
echo "按Ctrl+C停止系统"
echo ""

# 启动主程序
python3 main.py