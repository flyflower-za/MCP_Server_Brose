#!/bin/bash
# API使用测试脚本

BASE_URL="http://localhost:51234"
CONFIG_FILE=".test_config"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# 1. 登录函数
login() {
  log_info "正在登录..."
  response=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$1\",\"password\":\"$2\"}")

  token=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

  if [ -n "$token" ]; then
    echo "$token" > "$CONFIG_FILE"
    log_success "登录成功，Token已保存"
    return 0
  else
    log_error "登录失败"
    echo "响应: $response"
    return 1
  fi
}

# 2. 加载Token
load_token() {
  if [ -f "$CONFIG_FILE" ]; then
    cat "$CONFIG_FILE"
  else
    log_error "请先登录 (运行: $0 login)"
    exit 1
  fi
}

# 3. API调用通用函数
api_call() {
  local method=$1
  local endpoint=$2
  local data=$3
  local token=$(load_token)

  log_info "API调用: $method $endpoint"

  if [ -n "$data" ]; then
    curl -s -X "$method" "$BASE_URL$endpoint" \
      -H "Authorization: Bearer $token" \
      -H "Content-Type: application/json" \
      -d "$data"
  else
    curl -s -X "$method" "$BASE_URL$endpoint" \
      -H "Authorization: Bearer $token"
  fi
}

# 4. 格式化JSON输出
format_json() {
  python3 -m json.tool 2>/dev/null || cat
}

# 主命令处理
case "$1" in
  login)
    login "${2:-admin}" "${3:-mcp12345}"
    ;;

  statuses)
    api_call "GET" "/api/v1/servers/statuses" | format_json
    ;;

  status)
    if [ -z "$2" ]; then
      log_error "请指定服务器ID (例: $0 status pdf_extractor)"
      exit 1
    fi
    api_call "GET" "/api/v1/servers/$2/status" | format_json
    ;;

  restart)
    if [ -z "$2" ]; then
      log_error "请指定服务器ID (例: $0 restart qrcode_reader)"
      exit 1
    fi
    api_call "POST" "/api/v1/servers/$2/restart" | format_json
    ;;

  stop)
    if [ -z "$2" ]; then
      log_error "请指定服务器ID (例: $0 stop pdf_extractor)"
      exit 1
    fi
    api_call "POST" "/api/v1/servers/$2/stop" | format_json
    ;;

  start)
    if [ -z "$2" ]; then
      log_error "请指定服务器ID (例: $0 start pdf_extractor)"
      exit 1
    fi
    api_call "POST" "/api/v1/servers/$2/start" | format_json
    ;;

  system)
    api_call "GET" "/api/v1/system" | format_json
    ;;

  resources)
    api_call "GET" "/api/v1/system/resources" | format_json
    ;;

  pdf)
    if [ -z "$2" ]; then
      log_error "请指定PDF URL (例: $0 pdf https://example.com/doc.pdf)"
      exit 1
    fi
    api_call "POST" "/pdf/extract" "{\"url\":\"$2\"}" | format_json
    ;;

  qrcode)
    if [ -z "$2" ]; then
      log_error "请指定图片URL (例: $0 qrcode https://example.com/qrcode.png)"
      exit 1
    fi
    api_call "POST" "/qrcode/extract" "{\"image_url\":\"$2\"}" | format_json
    ;;

  health)
    curl -s "$BASE_URL/health" | format_json
    ;;

  token)
    token=$(load_token)
    log_info "当前Token:"
    echo "${token:0:50}..."
    ;;

  test)
    log_info "运行API测试套件..."
    echo ""

    # 测试1: 登录
    log_info "测试1: 登录"
    if login "admin" "mcp12345"; then
      log_success "登录测试通过"
    fi
    echo ""

    # 测试2: 获取服务器状态
    log_info "测试2: 获取服务器状态"
    api_call "GET" "/api/v1/servers/statuses" > /dev/null
    if [ $? -eq 0 ]; then
      log_success "服务器状态API正常"
    fi
    echo ""

    # 测试3: 系统信息
    log_info "测试3: 系统信息"
    api_call "GET" "/api/v1/system" > /dev/null
    if [ $? -eq 0 ]; then
      log_success "系统信息API正常"
    fi
    echo ""

    log_success "所有测试完成"
    ;;

  clean)
    rm -f "$CONFIG_FILE"
    log_success "配置文件已清理"
    ;;

  *)
    echo "MCP Servers Hub API 测试工具"
    echo ""
    echo "用法: $0 [命令] [参数...]"
    echo ""
    echo "认证命令:"
    echo "  $0 login [用户名] [密码]     # 登录获取Token"
    echo "  $0 token                    # 查看当前Token"
    echo "  $0 clean                    # 清理配置文件"
    echo ""
    echo "服务器管理:"
    echo "  $0 statuses                 # 查看所有服务器状态"
    echo "  $0 status <服务器ID>        # 查看单个服务器状态"
    echo "  $0 restart <服务器ID>       # 重启服务器"
    echo "  $0 stop <服务器ID>          # 停止服务器"
    echo "  $0 start <服务器ID>         # 启动服务器"
    echo ""
    echo "系统信息:"
    echo "  $0 system                   # 查看系统信息"
    echo "  $0 resources                # 查看系统资源"
    echo "  $0 health                   # 健康检查"
    echo ""
    echo "MCP服务:"
    echo "  $0 pdf <URL>                # PDF内容提取"
    echo "  $0 qrcode <URL>             # 二维码识别"
    echo ""
    echo "测试:"
    echo "  $0 test                     # 运行API测试套件"
    echo ""
    echo "示例:"
    echo "  $0 login                    # 使用默认凭据登录"
    echo "  $0 statuses                 # 查看所有服务器状态"
    echo "  $0 restart qrcode_reader    # 重启二维码识别器"
    echo "  $0 pdf https://example.com/doc.pdf  # 提取PDF内容"
    ;;
esac
