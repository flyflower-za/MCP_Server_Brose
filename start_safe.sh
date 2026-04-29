#!/bin/bash

###############################################################################
# MCP服务器安全启动脚本 v2.0
# 功能: 完整的依赖检查、端口管理、健康检查
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

###############################################################################
# 1. Python 版本检查
###############################################################################
check_python_version() {
    print_header "🐍 Python 版本检查"

    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    print_info "当前 Python 版本: $PYTHON_VERSION"

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "需要 Python 3.8 或更高版本"
        print_info "当前版本: $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python 版本符合要求 (≥3.8)"
}

###############################################################################
# 2. 虚拟环境检查
###############################################################################
check_virtual_env() {
    print_header "📦 虚拟环境检查"

    if [ ! -d "venv" ]; then
        print_error "未找到虚拟环境 venv"
        print_info "创建虚拟环境..."
        python3 -m venv venv
        print_success "虚拟环境创建完成"
    fi

    # 激活虚拟环境
    print_info "激活虚拟环境..."
    source venv/bin/activate

    # 验证虚拟环境
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "虚拟环境激活失败"
        exit 1
    fi

    print_success "虚拟环境已激活: $VIRTUAL_ENV"
}

###############################################################################
# 3. 依赖检查（使用 verify_deps.py）
###############################################################################
check_dependencies() {
    print_header "🔍 依赖检查"

    # 确保使用虚拟环境的 Python
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "虚拟环境未激活"
        exit 1
    fi

    # 使用虚拟环境的 python 和 pip
    VENV_PYTHON="$VIRTUAL_ENV/bin/python"
    VENV_PIP="$VIRTUAL_ENV/bin/pip"

    print_info "虚拟环境 Python: $VENV_PYTHON"
    print_info "虚拟环境 pip: $VENV_PIP"

    if [ ! -f "verify_deps.py" ]; then
        print_warning "未找到 verify_deps.py 脚本，直接安装依赖..."
    else
        print_info "运行依赖验证脚本..."
        if "$VENV_PYTHON" verify_deps.py > /dev/null 2>&1; then
            print_success "所有依赖已正确安装"
            return 0
        else
            print_warning "依赖检查失败，准备自动安装..."
        fi
    fi

    # 自动安装依赖（使用虚拟环境的 pip）
    print_info "正在安装依赖（这可能需要几分钟）..."
    echo ""

    if "$VENV_PIP" install -r requirements.txt; then
        echo ""
        print_success "依赖安装完成"

        # 再次验证
        if [ -f "verify_deps.py" ]; then
            print_info "验证安装结果..."
            if "$VENV_PYTHON" verify_deps.py > /dev/null 2>&1; then
                print_success "所有依赖验证通过"
            else
                print_warning "部分依赖可能未正确安装，但服务可能仍能运行"
            fi
        fi
    else
        print_error "依赖安装失败"
        print_info "请尝试手动安装: $VENV_PIP install -r requirements.txt"
        print_info "或使用国内镜像: $VENV_PIP install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt"
        exit 1
    fi
}

###############################################################################
# 4. 配置文件检查
###############################################################################
check_config() {
    print_header "⚙️  配置检查"

    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在"
        if [ -f ".env.example" ]; then
            print_info "从 .env.example 创建 .env 文件..."
            cp .env.example .env
            print_success ".env 文件已创建"
        else
            print_warning "使用默认配置"
        fi
    fi

    # 读取端口配置
    if [ -f ".env" ]; then
        PORT=$(grep "^MCP_PORT=" .env | cut -d'=' -f2 | tr -d ' ' | head -1)
        PORT=${PORT:-51234}
    else
        PORT=51234
    fi

    print_success "配置检查完成 (端口: $PORT)"
}

###############################################################################
# 5. 端口清理（增强版）
###############################################################################
cleanup_ports() {
    print_header "🧹 端口清理"

    # 清理主端口和MCP服务器端口（MCP_PORT+1 到 MCP_PORT+10）
    ports_to_clean=$PORT$(for i in $(seq 1 10); do echo " $(($PORT + $i))"; done)

    for port in $ports_to_clean; do
        if lsof -i :$port > /dev/null 2>&1; then
            print_info "端口 $port 被占用，正在清理..."
            PIDS=$(lsof -ti :$port 2>/dev/null)
            if [ -n "$PIDS" ]; then
                echo $PIDS | xargs kill -9 2>/dev/null || true
                sleep 0.5
                if ! lsof -i :$port > /dev/null 2>&1; then
                    print_success "端口 $port 已清理"
                else
                    print_warning "端口 $port 清理失败，可能需要手动处理"
                fi
            fi
        fi
    done

    print_success "端口清理完成"
}

###############################################################################
# 6. 系统资源检查
###############################################################################
check_system_resources() {
    print_header "💻 系统资源"

    # CPU 使用率
    if command -v python &> /dev/null; then
        python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%')" 2>/dev/null || print_info "CPU: N/A"
    fi

    # 内存使用
    if command -v free &> /dev/null; then
        free -h | grep "Mem:" || true
    elif [ "$(uname)" = "Darwin" ]; then
        # macOS
        VM_STATS=$(vm_stat)
        PAGE_SIZE=$(vm_stat | head -1 | sed 's/.*page size of \([0-9]*\).*/\1/')
        FREE_PAGES=$(echo "$VM_STATS" | grep "Pages free" | sed 's/.* \([0-9]*\).*/\1/')
        FREE_MEMORY=$((FREE_PAGES * PAGE_SIZE / 1024 / 1024))
        print_info "可用内存: ${FREE_MEMORY} MB"
    fi

    # 磁盘空间
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        print_warning "磁盘空间不足: ${DISK_USAGE}% 已使用"
    else
        print_success "磁盘空间充足: ${DISK_USAGE}% 已使用"
    fi
}

###############################################################################
# 7. 日志系统检查
###############################################################################
check_log_system() {
    print_header "📋 日志系统"

    LOG_DIR="logs"
    if [ ! -d "$LOG_DIR" ]; then
        print_info "创建日志目录..."
        mkdir -p "$LOG_DIR"
        print_success "日志目录已创建: $LOG_DIR"
    else
        # 检查日志文件大小
        if [ -f "$LOG_DIR/mcp_server.log" ]; then
            LOG_SIZE=$(du -h "$LOG_DIR/mcp_server.log" | cut -f1)
            print_info "当前日志大小: $LOG_SIZE"
        fi
        print_success "日志系统就绪"
    fi
}

###############################################################################
# 8. 显示启动信息
###############################################################################
show_startup_info() {
    print_header "🚀 启动信息"

    echo -e "${GREEN}服务地址:${NC}     http://localhost:$PORT"
    echo -e "${GREEN}API 文档:${NC}     http://localhost:$PORT/docs"
    echo -e "${GREEN}Dashboard:${NC}    http://localhost:$PORT/dashboard"
    echo -e "${GREEN}健康检查:${NC}     http://localhost:$PORT/health"
    echo ""
    echo -e "${BLUE}配置文件:${NC}     .env (PORT=$PORT)"
    echo -e "${BLUE}日志目录:${NC}     logs/"
    echo ""
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
    echo ""
}

###############################################################################
# 9. 启动后健康检查
###############################################################################
health_check_after_start() {
    print_header "🏥 健康检查"

    # 等待服务启动
    print_info "等待服务启动..."
    sleep 3

    # 检查主端口
    if lsof -i :$PORT > /dev/null 2>&1; then
        print_success "API 网关已启动 (端口 $PORT)"
    else
        print_error "API 网关启动失败"
        return 1
    fi

    # 检查健康端点
    print_info "检查健康端点..."
    if command -v curl &> /dev/null; then
        HEALTH_RESPONSE=$(curl -s http://localhost:$PORT/health 2>/dev/null || echo "")
        if [ -n "$HEALTH_RESPONSE" ]; then
            print_success "健康检查通过"
            echo "$HEALTH_RESPONSE" | python -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
        else
            print_warning "健康端点无响应"
        fi
    fi

    print_success "服务启动完成"
}

###############################################################################
# 主函数
###############################################################################
main() {
    clear

    echo -e "${BLUE}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           MCP Servers Hub 安全启动脚本 v2.0              ║
    ║                                                           ║
    ║                   🚀 准备启动服务 🚀                      ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    # 执行所有检查
    check_python_version
    check_virtual_env
    check_config
    check_dependencies
    check_system_resources
    check_log_system
    cleanup_ports
    show_startup_info

    # 启动服务器
    print_header "🎯 启动服务器"

    # 确保使用虚拟环境的 Python
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "虚拟环境未激活"
        exit 1
    fi

    VENV_PYTHON="$VIRTUAL_ENV/bin/python"
    print_info "使用 Python: $VENV_PYTHON"

    # 设置信号处理（优雅退出）
    trap 'echo ""; print_warning "正在停止服务器..."; exit 0' INT TERM

    # 启动并记录PID
    "$VENV_PYTHON" main.py &
    MAIN_PID=$!

    # 等待几秒让服务启动
    sleep 2

    # 执行健康检查
    if health_check_after_start; then
        echo ""
        print_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_success "  服务器已成功启动并运行在 PID: $MAIN_PID"
        print_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    else
        print_error "服务器启动失败，请检查日志: logs/mcp_server.log"
        kill $MAIN_PID 2>/dev/null || true
        exit 1
    fi

    # 等待主进程
    wait $MAIN_PID
}

###############################################################################
# 执行主函数
###############################################################################
main "$@"
