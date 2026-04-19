#!/bin/bash

# MCP服务器关闭脚本

echo "🛑 MCP服务器关闭"
echo "===================="

# 从.env读取端口
if [ -f ".env" ]; then
    PORT=$(grep "^MCP_PORT=" .env | cut -d'=' -f2 | tr -d ' ')
    PORT=${PORT:-51234}
else
    PORT=51234
fi

echo "📍 目标端口: $PORT"

# 1. 优先通过PID文件关闭（优雅退出）
if [ -f "logs/server.pid" ]; then
    PID=$(cat logs/server.pid)
    if kill -0 "$PID" 2>/dev/null; then
        echo "🔍 找到进程 PID=$PID，正在优雅关闭..."
        kill -SIGTERM "$PID" 2>/dev/null
        sleep 2

        # 检查是否已退出
        if kill -0 "$PID" 2>/dev/null; then
            echo "⚠️  进程未响应，强制终止..."
            kill -9 "$PID" 2>/dev/null
        fi
        rm -f logs/server.pid
        echo "✅ 进程已停止"
    else
        echo "⚠️  PID文件存在但进程已不在，清理PID文件..."
        rm -f logs/server.pid
    fi
fi

# 2. 按进程名关闭（兜底：处理 start_safe.sh 直接启动的情况）
PIDS=$(pgrep -f "python main.py" 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "🔍 发现 main.py 进程: $PIDS，正在关闭..."
    pkill -SIGTERM -f "python main.py" 2>/dev/null
    sleep 2
    # 仍未退出则强制
    pkill -9 -f "python main.py" 2>/dev/null
    echo "✅ 进程已终止"
fi

# 3. 按端口关闭（最终兜底）
PORT_PIDS=$(lsof -ti :$PORT 2>/dev/null)
if [ -n "$PORT_PIDS" ]; then
    echo "⚠️  端口 $PORT 仍有进程占用: $PORT_PIDS，强制释放..."
    echo "$PORT_PIDS" | xargs kill -9 2>/dev/null
    sleep 1
fi

# 4. 验证端口已释放
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "❌ 关闭失败，端口 $PORT 仍被占用"
    lsof -i :$PORT
    exit 1
else
    echo ""
    echo "✅ MCP服务器已完全关闭"
    echo "📍 端口 $PORT 已释放"
    echo "===================="
fi
