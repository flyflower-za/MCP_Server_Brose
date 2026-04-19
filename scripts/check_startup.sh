#!/bin/bash

# 进入项目根目录
cd "$(dirname "$0")/.."

echo "🔍 MCP服务器启动检查"
echo "===================="

# 从.env文件读取端口配置，默认8000
if [ -f ".env" ]; then
    PORT=$(grep "^MCP_PORT=" .env | cut -d'=' -f2 | tr -d ' ')
    PORT=${PORT:-8000}  # 如果为空，使用默认值8000
else
    PORT=8000
fi

echo "📍 检查端口: $PORT"
echo ""

# 1. 检查进程
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ 服务器进程运行中"
else
    echo "❌ 服务器进程未运行"
fi

# 2. 检查端口
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "✅ 端口$PORT已监听"
else
    echo "❌ 端口$PORT未监听"
fi

# 3. 检查HTTP响应
if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "✅ HTTP服务响应正常"

    # 4. 检查API端点
    servers_count=$(curl -s http://localhost:$PORT/ | grep -o '"loaded_servers":[0-9]*' | grep -o '[0-9]*')
    echo "✅ 已加载 $servers_count 个MCP服务器"
else
    echo "❌ HTTP服务无响应"
fi

echo "===================="
echo "📍 访问地址:"
echo "   主页: http://localhost:$PORT"
echo "   API文档: http://localhost:$PORT/docs"
echo "   健康检查: http://localhost:$PORT/health"
