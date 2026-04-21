# API 完整参考文档

**版本**: 1.0.0  
**更新**: 2026-04-22

---

## 📋 目录

- [API 认证说明](#api-认证说明)
- [服务器管理 API](#服务器管理-api)
- [端口配置 API](#端口配置-api)
- [配置管理 API](#配置管理-api)
- [系统监控 API](#系统监控-api)
- [认证 API](#认证-api)
- [状态码说明](#状态码说明)

---

## 🔐 API 认证说明

### **认证策略**

MCP Servers Hub 采用**分级认证策略**：

#### **无需认证**（开放调用）
适用于自动化工具、工作流、监控系统集成

```bash
# 直接调用，无需 Token
curl http://localhost:51234/api/v1/servers/statuses
```

#### **需要认证**（管理功能）
适用于 Dashboard 和配置管理

```bash
# 方法 1：JWT Token（推荐）
curl http://localhost:51234/api/v1/config/servers \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."

# 方法 2：Basic Auth（向后兼容）
curl http://localhost:51234/api/v1/config/servers \
  -u admin:brose123
```

---

## 🖥️ 服务器管理 API

### **获取所有服务器状态**

```http
GET /api/v1/servers/statuses
```

**认证**: 无需认证

**响应示例**:
```json
{
  "pdf_extractor": {
    "status": "running",
    "pid": 12345,
    "port": 51238,
    "uptime_seconds": 3600,
    "restart_count": 0,
    "last_restart_time": null
  }
}
```

---

### **获取单个服务器状态**

```http
GET /api/v1/servers/{server_id}/status
```

**参数**:
- `server_id` (路径参数) - 服务器 ID

**认证**: 无需认证

**响应示例**:
```json
{
  "status": "running",
  "pid": 12345,
  "port": 51238,
  "uptime_seconds": 3600,
  "restart_count": 0
}
```

---

### **启动服务器**

```http
POST /api/v1/servers/{server_id}/start
```

**参数**:
- `server_id` (路径参数) - 服务器 ID

**认证**: 无需认证

**响应示例**:
```json
{
  "success": true,
  "message": "服务器启动成功",
  "server_id": "pdf_extractor",
  "status": {
    "status": "running",
    "pid": 12346,
    "port": 51238
  }
}
```

---

### **停止服务器**

```http
POST /api/v1/servers/{server_id}/stop
```

**参数**:
- `server_id` (路径参数) - 服务器 ID

**认证**: 无需认证

**响应示例**:
```json
{
  "success": true,
  "message": "服务器停止成功",
  "server_id": "pdf_extractor",
  "status": {
    "status": "not_running"
  }
}
```

---

### **重启服务器**

```http
POST /api/v1/servers/{server_id}/restart
```

**参数**:
- `server_id` (路径参数) - 服务器 ID

**认证**: 无需认证

**响应示例**:
```json
{
  "success": true,
  "message": "服务器重启成功",
  "server_id": "pdf_extractor",
  "status": {
    "status": "running",
    "pid": 12347,
    "restart_count": 1
  }
}
```

---

### **启动所有服务器**

```http
POST /api/v1/servers/start-all
```

**认证**: 无需认证

**响应示例**:
```json
{
  "success": true,
  "started_count": 1,
  "failed_servers": [],
  "message": "已启动 1 个服务器"
}
```

---

### **停止所有服务器**

```http
POST /api/v1/servers/stop-all
```

**认证**: 无需认证

**响应示例**:
```json
{
  "success": true,
  "stopped_count": 1,
  "failed_servers": [],
  "message": "已停止 1 个服务器"
}
```

---

## 🔌 端口配置 API

### **获取所有端口配置**

```http
GET /api/v1/servers/port-configs
```

**认证**: 无需认证

**响应示例**:
```json
{
  "pdf_extractor": {
    "server_id": "pdf_extractor",
    "fixed_port": 51238,
    "mode": "fixed"
  },
  "web_scraper": {
    "server_id": "web_scraper",
    "fixed_port": null,
    "mode": "dynamic"
  }
}
```

---

### **获取单个端口配置**

```http
GET /api/v1/servers/{server_id}/port-config
```

**参数**:
- `server_id` (路径参数) - 服务器 ID

**认证**: 无需认证

**响应示例**:
```json
{
  "server_id": "pdf_extractor",
  "fixed_port": 51238,
  "mode": "fixed"
}
```

---

### **设置固定端口**

```http
PUT /api/v1/servers/{server_id}/port-config
```

**请求体**:
```json
{
  "port": 51240
}
```

**参数**:
- `server_id` (路径参数) - 服务器 ID
- `port` (请求体) - 端口号（1024-65535）

**认证**: 无需认证

**响应示例**:
```json
{
  "success": true,
  "server_id": "pdf_extractor",
  "fixed_port": 51240,
  "message": "固定端口已保存，重启后生效"
}
```

---

### **删除固定端口**

```http
DELETE /api/v1/servers/{server_id}/port-config
```

**参数**:
- `server_id` (路径参数) - 服务器 ID

**认证**: 无需认证

**响应示例**:
```json
{
  "success": true,
  "server_id": "pdf_extractor",
  "existed": true,
  "mode": "dynamic",
  "message": "固定端口已移除，下次启动将动态分配"
}
```

---

## ⚙️ 配置管理 API

### **获取所有服务器配置**

```http
GET /api/v1/config/servers
```

**认证**: 需要（Basic Auth 或 JWT Token）

**响应示例**:
```json
{
  "total": 1,
  "servers": {
    "pdf_extractor": {
      "id": "pdf_extractor",
      "name": "PDF Extractor",
      "description": "Get PDF content from URLs",
      "enabled": true,
      "version": "1.0.0",
      "module": "mcp_servers.pdf_extractor.server",
      "prefix": "/pdf",
      "tags": ["pdf", "extractor", "document"]
    }
  }
}
```

---

### **添加新服务器**

```http
POST /api/v1/config/servers?server_id={server_id}
```

**参数**:
- `server_id` (查询参数) - 服务器 ID
- `config` (请求体) - 服务器配置

**请求体**:
```json
{
  "name": "Web Scraper",
  "description": "Scrape web content",
  "module": "mcp_servers.web_scraper.server",
  "prefix": "/scraper",
  "tags": ["web", "scraper"],
  "enabled": true
}
```

**认证**: 需要

**响应示例**:
```json
{
  "success": true,
  "message": "服务器 web_scraper 已添加并保存",
  "server_id": "web_scraper",
  "config": { ... }
}
```

---

### **更新服务器配置**

```http
PUT /api/v1/config/servers/{server_id}
```

**参数**:
- `server_id` (路径参数) - 服务器 ID
- `config` (请求体) - 更新的配置（所有字段可选）

**请求体**:
```json
{
  "name": "New Name",
  "description": "New description",
  "enabled": false
}
```

**认证**: 需要

**响应示例**:
```json
{
  "success": true,
  "message": "服务器 pdf_extractor 配置已更新并保存",
  "server_id": "pdf_extractor",
  "config": { ... }
}
```

---

### **删除服务器**

```http
DELETE /api/v1/config/servers/{server_id}
```

**参数**:
- `server_id` (路径参数) - 服务器 ID

**认证**: 需要

**响应示例**:
```json
{
  "success": true,
  "message": "服务器 pdf_extractor 已删除并保存",
  "server_id": "pdf_extractor",
  "deleted_config": { ... }
}
```

---

### **启用/禁用服务器**

```http
PATCH /api/v1/config/servers/{server_id}/toggle?enabled={bool}
```

**参数**:
- `server_id` (路径参数) - 服务器 ID
- `enabled` (查询参数) - true（启用）或 false（禁用）

**认证**: 需要

**响应示例**:
```json
{
  "success": true,
  "message": "服务器 pdf_extractor 已禁用并保存",
  "server_id": "pdf_extractor",
  "enabled": false
}
```

---

### **导出所有配置**

```http
GET /api/v1/config/export
```

**认证**: 需要

**响应示例**:
```json
{
  "version": "1.0.0",
  "exported_at": "2026-04-22T12:00:00",
  "servers": { ... },
  "ports": { ... },
  "settings": { ... }
}
```

---

### **查看配置状态**

```http
GET /api/v1/config/status
```

**认证**: 需要

**响应示例**:
```json
{
  "config_dir": "/path/to/config",
  "servers_config_exists": true,
  "ports_config_exists": true,
  "settings_config_exists": false,
  "servers_count": 1,
  "ports_count": 1,
  "backups_count": 6
}
```

---

### **手动保存配置**

```http
POST /api/v1/config/save
```

**认证**: 需要

**响应示例**:
```json
{
  "success": true,
  "message": "配置已保存",
  "servers_saved": true,
  "ports_saved": true,
  "settings_saved": true
}
```

---

## 📊 系统监控 API

### **获取系统信息**

```http
GET /api/v1/system
```

**认证**: 无需认证

**响应示例**:
```json
{
  "system": "MCP Servers Hub",
  "version": "1.0.0",
  "status": "running",
  "api_prefix": "/api/v1",
  "architecture": "process_isolation",
  "loaded_servers": 1,
  "servers": { ... },
  "endpoints": { ... }
}
```

---

### **获取性能监控**

```http
GET /api/v1/system/resources
```

**认证**: 无需认证

**响应示例**:
```json
{
  "hub": {
    "cpu_percent": 2.3,
    "memory_mb": 128.5,
    "pid": 12345
  },
  "port_pool": {
    "base_port": 51235,
    "max_port": 51250,
    "allocated_count": 3,
    "total_ports": 16,
    "available_ports": 13,
    "allocated_ports": [51238, 51239, 51240]
  },
  "processes": {
    "total_processes": 1,
    "running_processes": 1,
    "max_restart": 3
  }
}
```

---

## 🔐 认证 API

### **登录**

```http
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "username": "admin",
  "password": "brose123"
}
```

**认证**: 无需认证（这是登录接口）

**响应示例**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### **验证 Token**

```http
POST /api/v1/auth/verify-token
```

**请求头**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**认证**: 需要（Bearer Token）

**响应示例**:
```json
{
  "username": "admin",
  "type": "access",
  "valid": true
}
```

---

### **修改密码**

```http
POST /api/v1/auth/change-password
```

**请求体**:
```json
{
  "old_password": "brose123",
  "new_password": "new_secure_password"
}
```

**认证**: 需要（Basic Auth 或 JWT Token）

**响应示例**:
```json
{
  "message": "Password changed successfully",
  "note": "Please update DASHBOARD_PASSWORD in your .env file for persistence"
}
```

---

## 📋 其他端点

### **健康检查**

```http
GET /health
```

**认证**: 无需认证

**响应示例**:
```json
{
  "status": "healthy",
  "architecture": "process_isolation",
  "loaded_servers": 1,
  "running_servers": 1,
  "servers": ["pdf_extractor"]
}
```

---

### **根路径**

```http
GET /
```

**认证**: 无需认证

**响应**: 重定向到 `/dashboard`

---

### **API 文档**

```http
GET /docs
```

**认证**: 无需认证

**响应**: Swagger UI 交互式文档

---

## 📊 状态码说明

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 200 | 成功 | 操作成功完成 |
| 400 | 请求错误 | 端口号超出范围 |
| 401 | 未授权 | Token 无效或过期 |
| 404 | 未找到 | 服务器不存在 |
| 422 | 验证失败 | 请求参数不符合要求 |
| 503 | 服务不可用 | 服务器未运行 |

---

## 🔧 使用示例

### **n8n 工作流**

```javascript
// HTTP Request 节点配置
方法: GET
URL: http://host.docker.internal:51234/api/v1/servers/statuses
认证: None

// 在 Switch 节点中判断
{{ $json["pdf_extractor"]["status"] === "running" }}
```

### **Python 脚本**

```python
import requests

# 获取所有服务器状态
response = requests.get("http://localhost:51234/api/v1/servers/statuses")
servers = response.json()

# 启动服务器
for server_id, status in servers.items():
    if status["status"] != "running":
        requests.post(f"http://localhost:51234/api/v1/servers/{server_id}/start")
```

### **Bash 脚本**

```bash
#!/bin/bash

# 启动所有服务器
curl -X POST http://localhost:51234/api/v1/servers/start-all

# 等待启动
sleep 5

# 检查状态
curl http://localhost:51234/api/v1/servers/statuses | jq .
```

---

## 📚 相关文档

- [配置持久化指南](CONFIG_PERSISTENCE.md)
- [N8N 集成指南](N8N_INTEGRATION.md)
- [端口管理指南](PORT_MANAGEMENT.md)

---

**最后更新**: 2026-04-22  
**API 版本**: 1.0.0
