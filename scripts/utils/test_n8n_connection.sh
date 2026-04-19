#!/bin/bash

# n8n连接测试脚本

echo "🔍 n8n连接配置检查"
echo "===================="

# 1. 检查服务器配置
echo "1️⃣ 服务器配置检查:"
if [ -f ".env" ]; then
    HOST=$(grep "MCP_HOST" .env | cut -d'=' -f2)
    PORT=$(grep "MCP_PORT" .env | cut -d'=' -f2)
    echo "   MCP_HOST: $HOST"
    echo "   MCP_PORT: $PORT"
else
    echo "   ❌ .env文件不存在"
fi

# 2. 检查服务器状态
echo ""
echo "2️⃣ 服务器状态检查:"
if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "   ✅ 服务器运行正常"
else
    echo "   ❌ 服务器未运行"
    echo "   请先启动: python main.py"
    exit 1
fi

# 3. 获取本地IP
echo ""
echo "3️⃣ 网络配置:"
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "无法获取")
if [ "$LOCAL_IP" != "无法获取" ]; then
    echo "   本地IP: $LOCAL_IP"
    echo "   访问地址: http://$LOCAL_IP:$PORT"
else
    echo "   无法自动获取本地IP"
    echo "   请手动查看: ifconfig | grep inet"
fi

# 4. 测试API端点
echo ""
echo "4️⃣ API端点测试:"
echo "   健康检查: http://localhost:$PORT/health"
echo "   PDF提取: http://localhost:$PORT/extract"
echo "   批量提取: http://localhost:$PORT/extract/batch"

# 5. n8n配置示例
echo ""
echo "5️⃣ n8n HTTP Request配置:"
echo "{"
echo "  \"method\": \"POST\","
echo "  \"url\": \"http://localhost:$PORT/extract\","
echo "  \"authentication\": \"none\","
echo "  \"requestBody\": {"
echo "    \"contentType\": \"application/json\","
echo "    \"body\": {"
echo "      \"url\": \"你的PDF_URL\","
echo "      \"include_metadata\": true"
echo "    }"
echo "  }"
echo "}"

echo ""
echo "===================="
echo "✅ 配置检查完成！"
echo ""
echo "📖 详细指南: docs/N8N_INTEGRATION.md"
