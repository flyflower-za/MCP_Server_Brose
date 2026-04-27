# 🔌 MCP Servers Hub - 端口管理完全指南

本指南详细介绍了MCP Servers Hub的端口管理机制，包括Hub主端口、MCP服务器端口池、固定端口配置等内容。

## 📋 目录

- [端口架构概述](#端口架构概述)
- [配置Hub主端口](#配置hub主端口)
- [MCP服务器端口分配](#mcp服务器端口分配)
- [固定端口配置](#固定端口配置)
- [端口冲突解决](#端口冲突解决)
- [生产环境建议](#生产环境建议)

---

## 🏗️ 端口架构概述

### 系统端口层次

```
┌─────────────────────────────────────────────┐
│  MCP Servers Hub 系统架构                    │
├─────────────────────────────────────────────┤
│                                             │
│  🌐 Hub 主端口 (MCP_PORT)                    │
│  ├─ 默认: 51234                            │
│  ├─ 用途: API网关、Dashboard                │
│  └─ 配置: .env 文件中的 MCP_PORT            │
│                                             │
│  🔧 MCP 服务器端口池 (PROCESS_BASE_PORT)     │
│  ├─ 基础端口: MCP_PORT + 1                  │
│  ├─ 用途: 各个MCP服务器进程                  │
│  ├─ 分配: 动态分配或固定端口                 │
│  └─ 配置: .env 文件中的 PROCESS_BASE_PORT    │
│                                             │
│  📦 单个服务器端口分配示例:                   │
│  ├─ PDF Extractor: 动态/固定                │
│  ├─ QR Code Reader: 动态/固定               │
│  └─ 其他服务器: 动态/固定                   │
│                                             │
└─────────────────────────────────────────────┘
```

### 端口配置文件

#### `.env` 配置示例
```bash
# Hub 主端口配置
MCP_PORT=51234              # API网关和Dashboard端口
MCP_HOST=0.0.0.0           # 监听地址

# MCP服务器端口池配置
PROCESS_BASE_PORT=51235    # 服务器基础端口
PROCESS_MAX_RESTART=3      # 最大重启次数
```

#### 端口分配逻辑
```python
# 动态端口分配算法
base_port = 51235  # PROCESS_BASE_PORT
server_count = 2   # 当前服务器数量

# 端口分配
pdf_extractor_port = base_port + 0     # 51235
qrcode_reader_port = base_port + 1    # 51236
# 新服务器继续递增...
```

---

## ⚙️ 配置Hub主端口

### 方法1: 编辑 .env 文件（推荐）

#### 修改步骤
```bash
# 1. 编辑配置文件
vim .env

# 2. 修改端口配置
MCP_PORT=8000  # 改为你想要的端口

# 3. 保存并重启服务器
./start_safe.sh
```

#### 完整配置示例
```bash
# .env 文件内容
MCP_HOST=0.0.0.0
MCP_PORT=8000          # Hub主端口
LOG_LEVEL=INFO
DEBUG=false

# 可选配置
PROCESS_BASE_PORT=8001 # 服务器端口池起始端口
```

### 方法2: 环境变量

#### 临时修改（当前会话）
```bash
# 直接设置环境变量启动
MCP_PORT=9000 python main.py

# 或使用export
export MCP_PORT=9000
python main.py
```

#### 永久修改（添加到Shell配置）
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo "export MCP_PORT=9000" >> ~/.zshrc
source ~/.zshrc

# 之后直接启动即可
python main.py
```

### 方法3: 命令行参数

#### 使用Uvicorn启动
```bash
# 指定端口和主机
uvicorn main:app --host 0.0.0.0 --port 9000

# 或使用完整参数
uvicorn main:app \
  --host 0.0.0.0 \
  --port 9000 \
  --log-level info \
  --reload
```

### 验证配置

#### 检查端口监听
```bash
# 查看端口占用
lsof -i :51234

# 或使用netstat
netstat -an | grep 51234

# 检查服务状态
curl http://localhost:51234/health
```

#### Dashboard访问
```bash
# 使用新端口访问
open http://localhost:8000/dashboard
```

---

## 🔧 MCP服务器端口分配

### 动态端口分配

#### 工作原理
```python
# 进程管理器自动分配端口
def allocate_port(server_id):
    """为服务器分配端口"""
    # 从PROCESS_BASE_PORT开始递增分配
    port = PROCESS_BASE_PORT + server_index
    return port
```

#### 查看当前端口分配
```bash
# 通过API查询
curl http://localhost:51234/api/v1/servers/statuses

# 或在Dashboard中查看
# 服务器卡片 -> 运行时信息 -> 当前端口
```

#### 端口分配示例
```json
{
  "pdf_extractor": {
    "port": 51235,
    "status": "running"
  },
  "qrcode_reader": {
    "port": 51236,
    "status": "running"
  }
}
```

### 固定端口配置

#### 为什么使用固定端口？
- ✅ **稳定性**: 服务重启后端口不变
- ✅ **可预测**: 客户端可以固定调用地址
- ✅ **防火墙**: 便于配置防火墙规则
- ✅ **负载均衡**: 便于配置反向代理

#### Dashboard配置

##### 图形界面配置
1. 登录Dashboard: `http://localhost:51234/dashboard`
2. 找到目标服务器卡片
3. 在**固定端口**配置区域:
   - 点击"✏️ 锁定/编辑"按钮
   - 输入端口号（1024-65535）
   - 点击"💾 保存"
4. 重启服务器使配置生效

##### API配置
```bash
# 设置固定端口
curl -X PUT http://localhost:51234/api/v1/servers/pdf_extractor/port-config \
  -H "Content-Type: application/json" \
  -d '{"port": 51235}'

# 删除固定端口（恢复动态分配）
curl -X DELETE http://localhost:51234/api/v1/servers/pdf_extractor/port-config
```

##### 配置文件存储
```bash
# 端口配置保存在 config/port_config.json
{
  "pdf_extractor": 51235,
  "qrcode_reader": 51236
}
```

### 端口模式对比

| 特性 | 动态分配 | 固定端口 |
|------|----------|----------|
| **配置复杂度** | 简单（自动） | 需要手动配置 |
| **端口稳定性** | 重启后可能变化 | 重启后保持不变 |
| **适用场景** | 开发环境 | 生产环境 |
| **客户端调用** | 需要动态查询 | 可以固定配置 |
| **防火墙规则** | 难以预设 | 可以预先配置 |

---

## 🛠️ 端口冲突解决

### 检测端口冲突

#### 系统命令检查
```bash
# macOS/Linux
lsof -i :51234

# 查看详细信息
lsof -i :51234 -n -P

# 检查端口范围
lsof -i :51234-51240
```

#### 使用脚本检查
```bash
# 使用项目提供的检查脚本
./scripts/check_startup.sh

# 输出示例
# ✓ Port 51234 is available
# ✗ Port 51235 is in use by process 12345
```

### 解决冲突方法

#### 方法1: 修改Hub端口
```bash
# 如果51234被占用，修改为其他端口
vim .env
# MCP_PORT=8000

./start_safe.sh
```

#### 方法2: 释放占用端口
```bash
# 1. 找到占用端口的进程
lsof -i :51234

# 2. 查看进程详情
ps aux | grep <PID>

# 3. 结束进程
kill <PID>
# 或强制结束
kill -9 <PID>
```

#### 方法3: 修改服务器端口池
```bash
# 如果基础端口冲突，修改端口池
vim .env
# PROCESS_BASE_PORT=52000  # 改为其他起始端口

./start_safe.sh
```

### 防止端口冲突

#### 规划端口使用
```bash
# 推荐端口范围分配
Hub主端口:     51234-51239
MCP服务器:     51240-51299
其他服务:      51300-51999
```

#### 自动端口选择
```bash
# 让系统自动选择可用端口
# 启动时如果端口冲突，会自动尝试附近端口
MCP_PORT=0  # 0表示让系统自动分配
```

---

## 🔐 生产环境建议

### 端口规划

#### 推荐配置
```bash
# .env 生产环境配置
MCP_PORT=80              # 使用标准HTTP端口
MCP_HOST=0.0.0.0
PROCESS_BASE_PORT=8080   # 服务器使用高位端口

# 安全配置
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=<strong_password>
JWT_SECRET_KEY=<random_32_char_key>
```

#### 重要服务器固定端口
```bash
# PDF Extractor
curl -X PUT http://localhost/api/v1/servers/pdf_extractor/port-config \
  -d '{"port": 8081}'

# QR Code Reader
curl -X PUT http://localhost/api/v1/servers/qrcode_reader/port-config \
  -d '{"port": 8082}'
```

### 反向代理配置

#### Nginx配置示例
```nginx
# /etc/nginx/sites-available/mcp-hub
server {
    listen 80;
    server_name your-domain.com;

    # Hub主服务
    location / {
        proxy_pass http://127.0.0.1:51234;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # PDF Extractor
    location /pdf/ {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host $host;
    }

    # QR Code Reader
    location /qrcode/ {
        proxy_pass http://127.0.0.1:8082/;
        proxy_set_header Host $host;
    }
}
```

#### SSL/HTTPS配置
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:51234;
        # ... 其他配置
    }
}
```

### 防火墙配置

#### UFW (Ubuntu)
```bash
# 允许HTTP端口
sudo ufw allow 80/tcp

# 允许HTTPS端口
sudo ufw allow 443/tcp

# 允许SSH（管理端口）
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable
```

#### firewalld (CentOS)
```bash
# 允许HTTP服务
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# 重载配置
sudo firewall-cmd --reload
```

### 监控和日志

#### 端口监控脚本
```bash
#!/bin/bash
# monitor_ports.sh
while true; do
    echo "=== Port Status $(date) ==="
    lsof -i :51234 -i :51235 -i :51236
    sleep 60
done
```

#### 日志监控
```bash
# 监控端口相关错误
tail -f logs/mcp_server.log | grep -i "port\|bind\|address"

# 监控启动失败
tail -f logs/mcp_server.log | grep -i "error\|failed"
```

---

## 📊 端口配置参考

### 端口分配建议

| 环境 | Hub端口 | 服务器端口池 | 说明 |
|------|---------|--------------|------|
| **开发** | 51234 | 51235+ | 默认配置，便于本地开发 |
| **测试** | 8000 | 8001+ | 标准端口，便于测试 |
| **生产** | 80 | 8080+ | HTTP标准端口，服务器使用高位 |
| **容器** | 8080 | 8081+ | 容器环境常用端口 |

### 端口范围规划

```
端口范围分配：
├─ 51234-51239: Hub和核心服务
├─ 51240-51299: MCP服务器（动态）
├─ 51300-51999: 预留扩展
└─ 8000-8999: 开发测试环境
```

### 端口配置最佳实践

#### ✅ 推荐做法
- 使用固定端口用于生产环境
- 在`.env`文件中集中管理端口配置
- 使用防火墙限制端口访问
- 定期检查端口占用情况
- 为不同环境使用不同端口范围

#### ❌ 避免做法
- 不要使用系统保留端口（< 1024）
- 不要随意修改已配置的固定端口
- 不要在生产环境使用动态端口（无特殊需求）
- 不要忽略端口冲突错误
- 不要在多个环境使用相同端口

---

## 🛠️ 故障排除

### 常见问题

#### Q: Hub启动后无法访问
```bash
# 检查端口是否正确
cat .env | grep MCP_PORT

# 检查服务是否监听
lsof -i :<MCP_PORT>

# 检查防火墙
sudo ufw status
```

#### Q: MCP服务器端口冲突
```bash
# 查看详细错误
tail -f logs/mcp_server.log

# 修改基础端口
vim .env
# PROCESS_BASE_PORT=52000

# 重启服务
./start_safe.sh
```

#### Q: 固定端口不生效
```bash
# 检查配置文件
cat config/port_config.json

# 确认服务器已重启
curl -X POST http://localhost:51234/api/v1/servers/<id>/restart

# 清除配置重新设置
curl -X DELETE http://localhost:51234/api/v1/servers/<id>/port-config
```

---

## 📚 相关文档

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 快速开始指南
- **[CONFIG_PERSISTENCE.md](CONFIG_PERSISTENCE.md)** - 配置持久化
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排除
- **[API_REFERENCE.md](API_REFERENCE.md)** - API参考手册

---

**💡 提示**: 合理的端口规划可以提高系统的稳定性和可维护性。在生产环境中，建议使用固定端口并配置适当的监控。

**🔒 安全提醒**: 确保只在必要时开放端口，并使用防火墙限制访问。
