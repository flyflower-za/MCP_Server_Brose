#!/bin/bash
# 测试 API 是否需要认证

echo "=== 测试 API 无需认证访问 ==="
echo ""

BASE_URL="http://localhost:51234"

echo "1. 测试健康检查（无需认证）"
curl -s -w "\n状态码: %{http_code}\n" "$BASE_URL/health"
echo ""

echo "2. 测试服务器状态列表（无需认证）"
curl -s -w "\n状态码: %{http_code}\n" "$BASE_URL/api/v1/servers/statuses"
echo ""

echo "3. 测试单个服务器状态（无需认证）"
curl -s -w "\n状态码: %{http_code}\n" "$BASE_URL/api/v1/servers/pdf_extractor/status"
echo ""

echo "4. 测试系统信息（无需认证）"
curl -s -w "\n状态码: %{http_code}\n" "$BASE_URL/api/v1/system"
echo ""

echo "=== 测试完成 ==="
