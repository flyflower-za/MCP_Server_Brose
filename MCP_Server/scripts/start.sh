#!/bin/bash

# 进入项目根目录
cd "$(dirname "$0")/.."

echo "=================================================="
echo "   MCP服务器管理系统"
echo "=================================================="
echo ""

# 激活虚拟环境
if [ -d ".venv" ]; then
    echo "📦 激活虚拟环境..."
    source .venv/bin/activate
else
    echo "⚠️  未找到虚拟环境，使用系统Python"
fi

# 检查依赖
echo "🔍 检查依赖..."
python -c "import fastapi, uvicorn, pypdf2, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 安装依赖..."
    pip install -q -r requirements.txt
fi

# 从.env读取端口
if [ -f ".env" ]; then
    PORT=$(grep "^MCP_PORT=" .env | cut -d'=' -f2 | tr -d ' ')
    HOST=$(grep "^MCP_HOST=" .env | cut -d'=' -f2 | tr -d ' ')
    PORT=${PORT:-8000}
    HOST=${HOST:-localhost}
else
    PORT=8000
    HOST=localhost
fi

echo ""
echo "🚀 启动MCP服务器..."
echo "📍 地址: http://$HOST:$PORT"
echo "📖 API文档: http://$HOST:$PORT/docs"
echo "⚙️  配置文件: .env (PORT=$PORT, HOST=$HOST)"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=================================================="
echo ""

# 启动主服务器
python main.py
