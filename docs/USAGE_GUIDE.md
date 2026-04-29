# MCP Servers Hub 使用指南

## 目录
- [快速开始](#快速开始)
- [认证方式](#认证方式)
- [API端点文档](#api端点文档)
- [云平台集成](#云平台集成)
- [故障排查](#故障排查)

---

## 快速开始

### 1. 启动服务

```bash
# macOS/Linux
./start_safe.sh

# 或手动启动
source .venv/bin/activate
python main.py
```

### 2. 访问Dashboard

打开浏览器访问：`http://localhost:51234/dashboard`

默认登录凭据：
- 用户名：`admin`
- 密码：`mcp12345`

### 3. 检查服务状态

```bash
curl http://localhost:51234/health
```

---

## 认证方式

系统支持两种认证方式，可根据使用场景选择：

### 方式一：API Key 认证（推荐用于插件集成）

**特点：**
- ✅ 永久有效，不会过期
- ✅ 适合自动化集成
- ✅ 无需定期刷新

**使用方法：**

在HTTP请求头中添加：
```http
Authorization: ApiKey q0X-8xtX7XwCkSYUtR2uSQmWx6f-eRE2DervK-mgiqE
```

**示例：**
```bash
curl -X GET http://localhost:51234/api/v1/servers/statuses \
  -H "Authorization: ApiKey q0X-8xtX7XwCkSYUtR2uSQmWx6f-eRE2DervK-mgiqE"
```

### 方式二：JWT Token 认证（推荐用于Dashboard登录）

**特点：**
- ✅ 24小时有效期
- ✅ 可主动刷新
- ✅ 安全性更高（会过期）

**获取Token：**

1. **Dashboard登录**：通过前端界面登录，自动获取Token
2. **API登录**：
```bash
curl -X POST http://localhost:51234/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "mcp12345"
  }'
```

**使用Token：**
```http
Authorization: Bearer YOUR_JWT_TOKEN
```

**刷新Token：**
```bash
curl -X POST http://localhost:51234/api/v1/auth/refresh \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## API端点文档

### 服务器管理API

#### 1. 查看所有服务器状态

```bash
GET /api/v1/servers/statuses
Authorization: ApiKey YOUR_API_KEY
```

**响应示例：**
```json
{
  "pdf_extractor": {
    "status": "running",
    "port": 51235,
    "pid": 12345,
    "uptime": "2 hours",
    "restart_count": 0
  },
  "qrcode_reader": {
    "status": "running",
    "port": 51236,
    "pid": 12346,
    "uptime": "2 hours",
    "restart_count": 0
  }
}
```

#### 2. 重启单个服务器

```bash
POST /api/v1/servers/{server_id}/restart
Authorization: ApiKey YOUR_API_KEY
```

**可用服务器ID：**
- `pdf_extractor` - PDF内容提取
- `qrcode_reader` - 二维码识别
- `pdf_signature_verifier` - PDF签章验证

#### 3. 停止单个服务器

```bash
POST /api/v1/servers/{server_id}/stop
Authorization: ApiKey YOUR_API_KEY
```

#### 4. 启动单个服务器

```bash
POST /api/v1/servers/{server_id}/start
Authorization: ApiKey YOUR_API_KEY
```

---

### PDF内容提取API

#### 从URL提取PDF内容

```bash
POST /pdf/extract
Authorization: ApiKey YOUR_API_KEY
Content-Type: application/json

{
  "url": "https://example.com/document.pdf",
  "include_metadata": true
}
```

**参数说明：**
- `url` (必需): PDF文件的URL地址
- `include_metadata` (可选): 是否包含元数据，默认true

**响应示例：**
```json
{
  "success": true,
  "content": "PDF文件的完整文本内容...",
  "metadata": {
    "title": "文档标题",
    "author": "作者",
    "pages": 10,
    "creation_date": "2024-01-01"
  }
}
```

#### 从Base64提取PDF内容

```bash
POST /pdf/extract
Authorization: ApiKey YOUR_API_KEY
Content-Type: application/json

{
  "base64": "JVBERi0xLjQKJ...",
  "include_metadata": false
}
```

---

### 二维码识别API

#### 从图片URL识别二维码

```bash
POST /qrcode/read
Authorization: ApiKey YOUR_API_KEY
Content-Type: application/json

{
  "url": "https://example.com/qrcode.png"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": [
    {
      "content": "https://example.com",
      "type": "QR_CODE",
      "position": {
        "x": 100,
        "y": 100,
        "width": 200,
        "height": 200
      }
    }
  ],
  "count": 1
}
```

#### 从Base64识别二维码

```bash
POST /qrcode/read
Authorization: ApiKey YOUR_API_KEY
Content-Type: application/json

{
  "base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

---

### PDF签章验证API

#### 验证PDF数字签名

```bash
POST /signature/verify
Authorization: ApiKey YOUR_API_KEY
Content-Type: application/json

{
  "url": "https://example.com/signed.pdf"
}
```

**响应示例：**
```json
{
  "success": true,
  "signatures": [
    {
      "signer": "CN=John Doe, O=Example Corp",
      "valid": true,
      "signing_time": "2024-01-01T10:00:00Z",
      "certificate_info": {
        "issuer": "CN=Example CA",
        "valid_from": "2023-01-01",
        "valid_to": "2025-01-01"
      }
    }
  ],
  "total_signatures": 1
}
```

---

## 云平台集成

### 百炼云平台配置

如果您使用百炼云平台集成MCP服务，请按以下方式配置：

#### 1. 获取API Key

```bash
# 从.env文件中获取
API_KEY=q0X-8xtX7XwCkSYUtR2uSQmWx6f-eRE2DervK-mgiqE
```

#### 2. 配置MCP服务器

在百炼云平台添加MCP服务器，使用以下JSON配置：

```json
{
  "name": "MCP Servers Hub",
  "url": "http://localhost:51234",
  "headers": {
    "Authorization": "ApiKey q0X-8xtX7XwCkSYUtR2uSQmWx6f-eRE2DervK-mgiqE"
  },
  "tools": [
    {
      "name": "extract_pdf",
      "description": "从PDF文件中提取文本内容",
      "endpoint": "/pdf/extract",
      "method": "POST"
    },
    {
      "name": "read_qrcode",
      "description": "从图片中识别二维码内容",
      "endpoint": "/qrcode/read",
      "method": "POST"
    }
  ]
}
```

#### 3. 调用示例

在百炼云平台的工作流中，可以这样调用：

```json
{
  "tool": "extract_pdf",
  "parameters": {
    "url": "{{workflow_input.pdf_url}}",
    "include_metadata": true
  },
  "authentication": {
    "type": "api_key",
    "header_name": "Authorization",
    "header_value": "ApiKey q0X-8xtX7XwCkSYUtR2uSQmWx6f-eRE2DervK-mgiqE"
  }
}
```

---

## 故障排查

### 问题1：认证失败 (401 Unauthorized)

**可能原因：**
- API Key不正确或未配置
- JWT Token已过期

**解决方案：**
```bash
# 检查API Key配置
echo $API_KEY

# 重新登录获取新Token
curl -X POST http://localhost:51234/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "mcp12345"}'
```

### 问题2：服务器未启动 (502 Bad Gateway)

**可能原因：**
- MCP服务器进程未运行
- 端口被占用

**解决方案：**
```bash
# 查看服务器状态
curl http://localhost:51234/api/v1/servers/statuses \
  -H "Authorization: ApiKey YOUR_API_KEY"

# 重启所有服务器
curl -X POST http://localhost:51234/api/v1/servers/start-all \
  -H "Authorization: ApiKey YOUR_API_KEY"

# 检查端口占用
lsof -i :51235
```

### 问题3：PDF提取失败

**可能原因：**
- PDF文件URL无法访问
- PDF文件已加密
- 文件大小超过限制

**解决方案：**
```bash
# 检查URL是否可访问
curl -I https://example.com/document.pdf

# 尝试使用Base64编码
base64 -i document.pdf > document.b64
# 然后使用base64参数调用API
```

### 问题4：二维码识别失败

**可能原因：**
- 图片格式不支持
- 二维码模糊或损坏
- 图片分辨率过低

**解决方案：**
```bash
# 确保图片清晰度
# 推荐格式：PNG, JPG
# 推荐分辨率：≥ 600x600
```

### 问题5：签章验证失败

**可能原因：**
- PDF文件未签名
- 证书链不完整
- 签名已过期

**注意：** macOS环境下PDF签章验证功能可能存在兼容性问题，建议在Linux环境使用。

---

## 配置参考

### 环境变量配置

```bash
# 服务器配置
MCP_HOST=0.0.0.0
MCP_PORT=51234

# 认证配置
DASHBOARD_AUTH_ENABLED=true
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=mcp12345

# JWT配置
JWT_SECRET_KEY=18TZk_mefnfPnIIFBWaGVE-GFtF0nkOptiHkWZ1q16w
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时

# API Key配置（永久有效）
API_KEY=q0X-8xtX7XwCkSYUtR2uSQmWx6f-eRE2DervK-mgiqE

# 模块启用配置
ENABLE_PDF_EXTRACTOR=true
ENABLE_QRCODE_READER=true
ENABLE_PDF_SIGNATURE_VERIFIER=false

# 进程管理配置
PROCESS_BASE_PORT=51235
PROCESS_AUTO_RESTART=true
PROCESS_START_TIMEOUT=30
```

### 修改API Key

如需更换API Key，请执行：

```bash
# 生成新的API Key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 更新.env文件中的API_KEY值
# 然后重启服务
./start_safe.sh
```

---

## 安全建议

1. **生产环境配置**
   - 修改默认密码（DASHBOARD_PASSWORD）
   - 使用强JWT密钥（JWT_SECRET_KEY）
   - 定期更换API Key
   - 启用HTTPS（配置SSL证书）

2. **访问控制**
   - 限制CORS来源（CORS_ORIGINS）
   - 配置防火墙规则
   - 使用反向代理（Nginx）

3. **日志监控**
   - 定期检查访问日志
   - 监控异常认证请求
   - 设置告警机制

---

## 联系支持

如有问题，请查看：
- 项目文档：`docs/`
- 日志文件：`logs/mcp_server.log`
- API文档：`http://localhost:51234/docs`

---

**最后更新：** 2026-04-29
**版本：** v1.0.0
