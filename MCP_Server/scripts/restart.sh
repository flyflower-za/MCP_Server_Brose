#!/bin/bash

# 进入项目根目录
cd "$(dirname "$0")/.."

echo "🔄 重启MCP服务器..."

# 停止当前服务器
pkill -f "python main.py"
sleep 2

# 从.env读取端口
if [ -f ".env" ]; then
    PORT=$(grep "^MCP_PORT=" .env | cut -d'=' -f2 | tr -d ' ')
    PORT=${PORT:-8000}
else
    PORT=8000
fi

# 启动服务器
nohup python main.py > logs/server.log 2>&1 &
echo $! > logs/server.pid

sleep 3

# 检查状态
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ 重启成功"
else
    echo "❌ 重启失败"
    echo "查看日志: tail logs/server.log"
fi
