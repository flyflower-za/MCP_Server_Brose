#!/bin/bash

# MCP服务器端口管理工具

show_menu() {
    echo "🔧 MCP服务器端口管理工具"
    echo "========================"
    echo "1. 查看当前端口配置"
    echo "2. 修改端口配置"
    echo "3. 检查端口占用"
    echo "4. 查找可用端口"
    echo "5. 清理占用端口"
    echo "6. 快速启动(指定端口)"
    echo "0. 退出"
    echo "========================"
}

show_current_config() {
    echo "📋 当前端口配置:"
    echo "========================"
    grep -n "PORT\|HOST" config/settings.py | head -5
    echo ""
    echo "环境变量:"
    echo "MCP_PORT: ${MCP_PORT:-未设置}"
    echo "MCP_HOST: ${MCP_HOST:-未设置}"
}

modify_port_config() {
    read -p "请输入新端口号: " new_port

    if [[ ! $new_port =~ ^[0-9]+$ ]] || [ $new_port -lt 1024 ] || [ $new_port -gt 65535 ]; then
        echo "❌ 无效的端口号 (1024-65535)"
        return
    fi

    echo "你选择的端口: $new_port"

    # 检查端口是否被占用
    if lsof -i :$new_port > /dev/null 2>&1; then
        echo "⚠️  端口 $new_port 已被占用"
        read -p "是否强制使用? (y/n): " force
        if [ "$force" != "y" ]; then
            return
        fi
    fi

    echo "选择修改方式:"
    echo "1. 临时修改(环境变量)"
    echo "2. 永久修改(配置文件)"

    read -p "请选择 (1/2): " choice

    case $choice in
        1)
            echo "export MCP_PORT=$new_port" >> ~/.bashrc
            echo "✅ 已添加到 ~/.bashrc，请运行: source ~/.bashrc"
            ;;
        2)
            sed -i.bak "s/PORT: int = int(os.getenv(\"MCP_PORT\", \"[0-9]*\"))/PORT: int = int(os.getenv(\"MCP_PORT\", \"$new_port\"))/" config/settings.py
            echo "✅ 已修改 config/settings.py"
            echo "原文件已备份为: config/settings.py.bak"
            ;;
    esac
}

check_port_occupancy() {
    read -p "请输入要检查的端口号: " port

    echo "🔍 检查端口 $port..."

    if lsof -i :$port > /dev/null 2>&1; then
        echo "✅ 端口 $port 正在使用"
        echo "详细信息:"
        lsof -i :$port
    else
        echo "❌ 端口 $port 空闲"
    fi
}

find_available_port() {
    read -p "请输入端口范围起始 (默认8000): " start
    start=${start:-8000}

    read -p "请输入端口范围结束 (默认8100): " end
    end=${end:-8100}

    echo "🔍 在 $start-$end 范围内查找可用端口..."

    for port in $(seq $start $end); do
        if ! lsof -i :$port > /dev/null 2>&1; then
            echo "✅ 找到可用端口: $port"
            return
        fi
    done

    echo "❌ 未找到可用端口"
}

clean_port() {
    read -p "请输入要清理的端口号: " port

    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  端口 $port 正在使用"
        read -p "确认停止? (y/n): " confirm

        if [ "$confirm" = "y" ]; then
            lsof -ti :$port | xargs kill -9
            echo "✅ 已清理端口 $port"
        fi
    else
        echo "❌ 端口 $port 未被占用"
    fi
}

quick_start() {
    read -p "请输入端口号: " port

    if [ -z "$port" ]; then
        echo "❌ 端口号不能为空"
        return
    fi

    echo "🚀 使用端口 $port 启动MCP服务器..."

    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用，正在清理..."
        lsof -ti :$port | xargs kill -9 2>/dev/null
        sleep 2
    fi

    MCP_PORT=$port python main.py
}

# 主循环
while true; do
    show_menu
    read -p "请选择操作: " choice

    case $choice in
        1) show_current_config ;;
        2) modify_port_config ;;
        3) check_port_occupancy ;;
        4) find_available_port ;;
        5) clean_port ;;
        6) quick_start ;;
        0) echo "👋 再见！"; exit 0 ;;
        *) echo "❌ 无效选择" ;;
    esac

    echo ""
    read -p "按回车继续..."
    clear
done
