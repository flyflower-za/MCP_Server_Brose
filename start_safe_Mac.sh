#!/bin/bash

# MCP服务器安全启动脚本

echo "🚀 MCP服务器安全启动"
echo "===================="

# 1. 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 未找到虚拟环境"
    exit 1
fi

# 2. 激活虚拟环境
echo "📦 激活虚拟环境..."
source .venv/bin/activate

# 3. 检查依赖
echo "🔍 检查依赖..."
python -c "import fastapi, uvicorn, pypdf2, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 安装依赖..."
    pip install -q -r requirements.txt
fi

# 4. 检查端口（从.env读取）
if [ -f ".env" ]; then
    PORT=$(grep "^MCP_PORT=" .env | cut -d'=' -f2 | tr -d ' ')
    PORT=${PORT:-51234}
else
    PORT=51234
fi

# 清理主端口和MCP服务器端口（MCP_PORT+1 到 MCP_PORT+10）
echo "🧹 检查并清理端口..."
for port in $PORT $(seq $((PORT + 1)) $((PORT + 10))); do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  端口$port被占用，正在清理..."
        lsof -ti :$port | xargs kill -9 2>/dev/null
        sleep 0.5
        echo "✅ 端口$port已清理"
    fi
done

# 5. 显示启动信息
echo ""
echo "🚀 启动MCP服务器..."
echo "📍 地址: http://localhost:$PORT"
echo "📖 API文档: http://localhost:$PORT/docs"
echo "⚙️  配置文件: .env (PORT=$PORT)"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "===================="
echo ""

# 6. 启动服务器
python main.py
