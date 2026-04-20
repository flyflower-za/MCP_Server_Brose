#!/bin/bash

# MCP服务器停止脚本
# 彻底清理所有相关进程

echo "🛑 停止 MCP 服务器"
echo "========================================"

# 1. 从 .env 读取端口
if [ -f ".env" ]; then
    PORT=$(grep "^MCP_PORT=" .env | cut -d'=' -f2 | tr -d ' ')
    PORT=${PORT:-51234}
else
    PORT=51234
fi

# 2. 停止主进程（Hub）
echo ""
echo "📡 停止 API 网关 (端口 $PORT)..."
HUB_PIDS=$(lsof -ti :$PORT 2>/dev/null)
if [ -n "$HUB_PIDS" ]; then
    echo "$HUB_PIDS" | xargs kill -9 2>/dev/null
    echo "✅ 已停止 API 网关"
else
    echo "ℹ️  API 网关未运行"
fi

# 3. 停止所有 MCP 服务器进程（51235-51299 范围）
echo ""
echo "🧩 停止 MCP 服务器进程..."
for p in $(seq 51235 51299); do
    PIDS=$(lsof -ti :$p 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null
        echo "✅ 已停止端口 $p 上的进程"
    fi
done

# 4. 停止所有 server_launcher 进程
echo ""
echo "🔧 停止 server_launcher 子进程..."
LAUNCHER_PIDS=$(pgrep -f "server_launcher" 2>/dev/null)
if [ -n "$LAUNCHER_PIDS" ]; then
    echo "$LAUNCHER_PIDS" | xargs kill -9 2>/dev/null
    echo "✅ 已停止 server_launcher 进程"
else
    echo "ℹ️  没有运行中的 server_launcher 进程"
fi

# 5. 停止所有 main.py 进程
echo ""
echo "📋 停止 main.py 进程..."
MAIN_PIDS=$(pgrep -f "main.py" 2>/dev/null)
if [ -n "$MAIN_PIDS" ]; then
    echo "$MAIN_PIDS" | xargs kill -9 2>/dev/null
    echo "✅ 已停止 main.py 进程"
else
    echo "ℹ️  没有运行中的 main.py 进程"
fi

# 6. 等待进程完全退出
echo ""
echo "⏳ 等待进程完全退出..."
sleep 2

# 7. 验证清理结果
echo ""
echo "🔍 验证清理结果..."
REMAINING=0

# 检查主端口
if lsof -ti :$PORT > /dev/null 2>&1; then
    echo "⚠️  端口 $PORT 仍被占用"
    REMAINING=1
else
    echo "✅ 端口 $PORT 已释放"
fi

# 检查服务器端口范围
for p in $(seq 51235 51299); do
    if lsof -ti :$p > /dev/null 2>&1; then
        echo "⚠️  端口 $p 仍被占用"
        REMAINING=1
    fi
done

# 8. 清理 PID 文件
echo ""
if [ -f "logs/server.pid" ]; then
    rm -f logs/server.pid
    echo "🗑️  已清理 PID 文件"
fi

echo ""
echo "========================================"
if [ $REMAINING -eq 0 ]; then
    echo "✅ 所有进程已停止"
    echo "✅ 端口已全部释放"
else
    echo "⚠️  部分进程仍在运行"
    echo "请手动检查: lsof -i :$PORT"
fi
echo "========================================"
