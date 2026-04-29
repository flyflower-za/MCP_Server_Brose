# MCP Servers Hub API 使用指南

## 🔐 认证流程

### 1. 登录获取JWT Token

**请求示例**：
```bash
curl -X POST http://localhost:51234/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"mcp12345"}'
```

**响应示例**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. 使用Token进行API调用

在后续请求中添加 Authorization 头：
```bash
curl -X GET http://localhost:51234/api/v1/servers/statuses \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📡 API 端点列表

### 系统管理 API

#### 1. 查看所有服务器状态
```bash
GET /api/v1/servers/statuses
Authorization: Bearer {token}

# 响应：
{
  "pdf_extractor": {
    "server_id": "pdf_extractor",
    "status": "running",
    "pid": 12345,
    "port": 51235,
    "start_time": "2026-04-29T20:24:12.631287",
    "restart_count": 0,
    "uptime_seconds": 123.45
  }
}
```

#### 2. 查看单个服务器状态
```bash
GET /api/v1/servers/{server_id}/status
Authorization: Bearer {token}

# 示例：
curl -X GET http://localhost:51234/api/v1/servers/pdf_extractor/status \
  -H "Authorization: Bearer {token}"
```

#### 3. 重启服务器
```bash
POST /api/v1/servers/{server_id}/restart
Authorization: Bearer {token}

# 示例：
curl -X POST http://localhost:51234/api/v1/servers/qrcode_reader/restart \
  -H "Authorization: Bearer {token}"

# 响应：
{
  "success": true,
  "message": "服务器重启成功",
  "server_id": "qrcode_reader",
  "status": { ... }
}
```

#### 4. 停止服务器
```bash
POST /api/v1/servers/{server_id}/stop
Authorization: Bearer {token}

# 示例：
curl -X POST http://localhost:51234/api/v1/servers/pdf_extractor/stop \
  -H "Authorization: Bearer {token}"
```

#### 5. 启动服务器
```bash
POST /api/v1/servers/{server_id}/start
Authorization: Bearer {token}

# 示例：
curl -X POST http://localhost:51234/api/v1/servers/pdf_extractor/start \
  -H "Authorization: Bearer {token}"
```

### 系统信息 API

#### 6. 查看系统信息
```bash
GET /api/v1/system
Authorization: Bearer {token}

# 响应：
{
  "system": "MCP Servers Hub",
  "version": "1.0.0",
  "status": "running",
  "loaded_servers": 3,
  "auth_enabled": true
}
```

#### 7. 查看系统资源
```bash
GET /api/v1/system/resources
Authorization: Bearer {token}

# 响应：
{
  "hub": {
    "cpu_percent": 0.0,
    "memory_mb": 33.75,
    "pid": 12345
  },
  "port_pool": {
    "base_port": 51235,
    "allocated_count": 3,
    "available_ports": 14298
  }
}
```

### MCP 服务器 API

#### 8. PDF 提取器
```bash
POST /pdf/extract
Authorization: Bearer {token}
Content-Type: application/json

# 请求体：
{
  "url": "https://example.com/document.pdf"
}

# 响应：
{
  "success": true,
  "url": "https://example.com/document.pdf",
  "total_pages": 1,
  "content": "PDF 文档内容...",
  "metadata": {
    "title": "文档标题",
    "author": "作者",
    "creator": "创建工具"
  }
}
```

#### 9. 二维码识别器
```bash
POST /qrcode/extract
Authorization: Bearer {token}
Content-Type: application/json

# 请求体：
{
  "image_url": "https://example.com/qrcode.png"
}

# 响应：
{
  "success": true,
  "content": ["二维码内容1", "二维码内容2"]
}
```

#### 10. PDF 签章验证器
```bash
POST /signature/verify
Authorization: Bearer {token}
Content-Type: application/json

# 请求体：
{
  "url": "https://example.com/signed.pdf"
}

# 响应：
{
  "success": true,
  "valid": true,
  "signatures": [...]
}
```

---

## 💻 编程语言示例

### Python 示例

```python
import requests
import json

BASE_URL = "http://localhost:51234"

# 1. 登录获取Token
def login(username, password):
    response = requests.post(f"{BASE_URL}/api/v1/auth/login",
                           json={"username": username, "password": password})
    return response.json()["access_token"]

# 2. 查看服务器状态
def get_server_statuses(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/servers/statuses",
                           headers=headers)
    return response.json()

# 3. 重启服务器
def restart_server(token, server_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/v1/servers/{server_id}/restart",
                            headers=headers)
    return response.json()

# 4. PDF提取
def extract_pdf(token, pdf_url):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"url": pdf_url}
    response = requests.post(f"{BASE_URL}/pdf/extract",
                            headers=headers,
                            json=data)
    return response.json()

# 使用示例
token = login("admin", "mcp12345")
statuses = get_server_statuses(token)
print(json.dumps(statuses, indent=2, ensure_ascii=False))

# PDF提取
pdf_result = extract_pdf(token, "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
print(f"PDF内容: {pdf_result['content']}")
```

### JavaScript/Node.js 示例

```javascript
const BASE_URL = 'http://localhost:51234';

// 1. 登录获取Token
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  return data.access_token;
}

// 2. 查看服务器状态
async function getServerStatuses(token) {
  const response = await fetch(`${BASE_URL}/api/v1/servers/statuses`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 3. 重启服务器
async function restartServer(token, serverId) {
  const response = await fetch(`${BASE_URL}/api/v1/servers/${serverId}/restart`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 4. PDF提取
async function extractPDF(token, pdfUrl) {
  const response = await fetch(`${BASE_URL}/pdf/extract`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url: pdfUrl })
  });
  return await response.json();
}

// 使用示例
(async () => {
  const token = await login('admin', 'mcp12345');
  const statuses = await getServerStatuses(token);
  console.log(JSON.stringify(statuses, null, 2));

  const pdfResult = await extractPDF(token, 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf');
  console.log('PDF内容:', pdfResult.content);
})();
```

### Bash/Curl 脚本示例

```bash
#!/bin/bash

BASE_URL="http://localhost:51234"

# 1. 登录获取Token
login() {
  curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$1\",\"password\":\"$2\"}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])"
}

# 2. 获取服务器状态
get_statuses() {
  local token=$1
  curl -s -X GET "$BASE_URL/api/v1/servers/statuses" \
    -H "Authorization: Bearer $token" \
    | python3 -m json.tool
}

# 3. 重启服务器
restart_server() {
  local token=$1
  local server_id=$2
  curl -s -X POST "$BASE_URL/api/v1/servers/$server_id/restart" \
    -H "Authorization: Bearer $token" \
    | python3 -m json.tool
}

# 4. PDF提取
extract_pdf() {
  local token=$1
  local pdf_url=$2
  curl -s -X POST "$BASE_URL/pdf/extract" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"$pdf_url\"}" \
    | python3 -m json.tool
}

# 使用示例
TOKEN=$(login "admin" "mcp12345")
echo "获取Token: ${TOKEN:0:20}..."

echo "服务器状态:"
get_statuses "$TOKEN"

echo "重启PDF提取器:"
restart_server "$TOKEN" "pdf_extractor"

echo "PDF提取:"
extract_pdf "$TOKEN" "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
```

---

## 🔧 常见使用场景

### 场景1：监控服务器状态

```bash
# 获取Token
TOKEN=$(curl -s -X POST http://localhost:51234/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"mcp12345"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 检查所有服务器状态
curl -s -X GET http://localhost:51234/api/v1/servers/statuses \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

### 场景2：批量重启失败的服务器

```python
import requests

token = login("admin", "mcp12345")
statuses = get_server_statuses(token)

for server_id, status in statuses.items():
    if status["status"] != "running":
        print(f"重启失败的服务器: {server_id}")
        restart_server(token, server_id)
```

### 场景3：定时检查系统健康

```bash
#!/bin/bash
# 健康检查脚本

TOKEN=$(login "admin" "mcp12345")

# 检查系统资源
curl -s -X GET http://localhost:51234/api/v1/system/resources \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

# 检查服务器状态
curl -s -X GET http://localhost:51234/api/v1/servers/statuses \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

---

## ⚠️ 错误处理

### Token 过期

当Token过期时，API会返回401错误：
```json
{
  "detail": "Authentication required",
  "message": "请先登录访问此资源",
  "auth_enabled": true
}
```

**解决方案**：重新登录获取新Token。

### 无效请求

```json
{
  "detail": "Invalid authentication credentials"
}
```

**解决方案**：检查用户名密码是否正确。

---

## 📝 最佳实践

1. **Token存储**：将Token安全存储在环境变量或配置文件中
2. **错误重试**：实现Token过期自动重新获取机制
3. **连接池**：使用HTTP连接池提高性能
4. **超时设置**：为长时间运行的操作设置合理超时
5. **日志记录**：记录API调用和错误信息便于调试

---

## 🔗 相关链接

- API文档: http://localhost:51234/docs
- Dashboard: http://localhost:51234/dashboard
- 健康检查: http://localhost:51234/health
