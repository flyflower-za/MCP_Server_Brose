#!/bin/bash
###############################################################################
# MCP Server Hub 项目清理脚本
###############################################################################
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0;0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           MCP Servers Hub 项目清理工具 v1.0               ║${NC}"
echo -e "${BLUE}║              🧹 清理不需要的项目文件 🧹                  ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}\n"

print_warning "此操作将删除备份文件和缓存，但不会影响项目功能"
read -p "按回车继续，Ctrl+C 取消..."

# 1. 清理备份文件
print_header "🗑️  清理备份文件"
backup_count=0
for file in $(find . -type f \( -name "*.backup" -o -name "*.bak" -o -name "*~" \) | grep -v ".venv" | grep -v ".git"); do
    if [ -f "$file" ]; then
        rm -f "$file"
        backup_count=$((backup_count + 1))
        print_info "删除: $file"
    fi
done
if [ $backup_count -gt 0 ]; then
    print_success "已删除 $backup_count 个备份文件"
else
    print_info "没有找到备份文件"
fi

# 2. 清理 Python 缓存
print_header "🐍 清理 Python 缓存"
cache_count=0
for cache_dir in $(find . -type d -name "__pycache__" | grep -v ".venv" | grep -v ".git"); do
    rm -rf "$cache_dir"
    cache_count=$((cache_count + 1))
    print_info "删除: $cache_dir"
done
for pyc_file in $(find . -type f -name "*.pyc" | grep -v ".venv" | grep -v ".git"); do
    rm -f "$pyc_file"
    cache_count=$((cache_count + 1))
done
if [ -d ".pytest_cache" ]; then
    rm -rf ".pytest_cache"
    cache_count=$((cache_count + 1))
fi
if [ $cache_count -gt 0 ]; then
    print_success "已删除 $cache_count 个缓存项"
else
    print_info "没有找到 Python 缓存"
fi

# 3. 清理系统临时文件
print_header "🧹 清理系统临时文件"
temp_count=0
for ds_store in $(find . -name ".DS_Store" | grep -v ".venv" | grep -v ".git"); do
    rm -f "$ds_store"
    temp_count=$((temp_count + 1))
    print_info "删除: $ds_store"
done
if [ $temp_count -gt 0 ]; then
    print_success "已删除 $temp_count 个系统临时文件"
else
    print_info "没有找到系统临时文件"
fi

# 4. 清理临时脚本
print_header "📜 清理临时脚本"
if [ -f "install_deps_fast.sh" ]; then
    rm -f "install_deps_fast.sh"
    print_info "删除: install_deps_fast.sh"
fi
if [ -f "start_safe.sh" ] && [ -f "start_safe_Mac_v2.sh" ]; then
    [ ! -f "start_safe.sh.old" ] && mv start_safe.sh start_safe.sh.old
    print_info "备份: start_safe.sh → start_safe.sh.old"
fi
print_success "临时脚本处理完成"

# 5. 显示总结
print_header "📊 清理总结"
project_size=$(du -sh . | cut -f1)
venv_size=$(du -sh .venv 2>/dev/null | cut -f1)
log_size=$(du -sh logs 2>/dev/null | cut -f1)
echo -e "${BLUE}当前磁盘使用:${NC}"
echo "  📁 项目总大小: $project_size"
echo "  🐍 虚拟环境: $venv_size"
echo "  📋 日志目录: $log_size"
echo ""
print_success "项目清理完成！"
