# MCP Servers Hub - 统一管理平台

**版本**: 1.0.0  
**架构**: 进程隔离 + API网关  
**状态**: ✅ 生产就绪

> 🎯 **统一管理多个 MCP 服务器，支持启停控制、端口管理、性能监控、配置持久化**

---

## ✨ 核心特性

### 🚀 **开箱即用**
- ✅ **零配置启动** - 一条命令启动所有服务
- ✅ **配置持久化** - 重启后配置不丢失
- ✅ **自动端口分配** - 智能分配端口，避免冲突
- ✅ **自动恢复** - 服务崩溃自动重启

### 🎛️ **可视化管理**
- ✅ **Dashboard 控制台** - 现代化 Web 界面
- ✅ **实时监控** - CPU、内存、端口池状态
- ✅ **搜索过滤** - 快速找到目标服务器
- ✅ **配置管理** - 可视化添加/编辑/删除服务器

### 🔐 **安全认证**
- ✅ **JWT Token 登录** - 安全的身份验证
- ✅ **权限分级** - 管理功能需认证，API 开放调用
- ✅ **密码哈希** - 不存储明文密码

### 📊 **可观测性**
- ✅ **性能监控** - 实时系统资源监控
- ✅ **操作日志** - 详细的操作记录
- ✅ **健康检查** - 服务状态实时检测
- ✅ **配置导出** - 一键导出完整配置

---

## 🚀 快速开始

### **1. 安装依赖**

```bash
# 克隆项目
git clone <repo-url>
cd MCP_Server_Brose

# 安装依赖
pip install -r requirements.txt
```

### **2. 启动服务**

```bash
# 使用安全启动脚本（推荐）
bash start_safe.sh

# 或直接运行
python main.py
```

### **3. 访问服务**

```bash
# Dashboard（需要登录）
http://localhost:51234/dashboard

# API 文档
http://localhost:51234/docs

# 健康检查
http://localhost:51234/health
```

### **4. 默认登录凭据**

```
用户名: admin
密码: brose123
```

⚠️ **生产环境请立即修改密码！**

---

## 📖 功能总览

### **服务器管理**

| 功能 | API | 说明 |
|------|-----|------|
| 查看所有服务器 | `GET /api/v1/servers` | 列出服务器状态 |
| 查看服务器状态 | `GET /api/v1/servers/{id}/status` | 详细状态信息 |
| 启动服务器 | `POST /api/v1/servers/{id}/start` | 启动单个服务器 |
| 停止服务器 | `POST /api/v1/servers/{id}/stop` | 停止单个服务器 |
| 重启服务器 | `POST /api/v1/servers/{id}/restart` | 重启单个服务器 |
| 启动全部 | `POST /api/v1/servers/start-all` | 批量启动 |
| 停止全部 | `POST /api/v1/servers/stop-all` | 批量停止 |

### **端口管理**

| 功能 | API | 说明 |
|------|-----|------|
| 查看端口配置 | `GET /api/v1/servers/port-configs` | 所有端口配置 |
| 获取固定端口 | `GET /api/v1/servers/{id}/port-config` | 查询端口 |
| 设置固定端口 | `PUT /api/v1/servers/{id}/port-config` | 固定端口 |
| 删除固定端口 | `DELETE /api/v1/servers/{id}/port-config` | 恢复动态分配 |

### **配置管理**

| 功能 | API | 说明 |
|------|-----|------|
| 查看配置 | `GET /api/v1/config/servers` | 所有服务器配置 |
| 添加服务器 | `POST /api/v1/config/servers?id={id}` | 新建服务器 |
| 更新服务器 | `PUT /api/v1/config/servers/{id}` | 更新配置 |
| 删除服务器 | `DELETE /api/v1/config/servers/{id}` | 删除配置 |
| 启用/禁用 | `PATCH /api/v1/config/servers/{id}/toggle` | 切换状态 |
| 导出配置 | `GET /api/v1/config/export` | 导出所有配置 |
| 保存配置 | `POST /api/v1/config/save` | 手动保存到磁盘 |

### **系统监控**

| 功能 | API | 说明 |
|------|-----|------|
| 系统信息 | `GET /api/v1/system` | 系统版本和状态 |
| 性能监控 | `GET /api/v1/system/resources` | CPU、内存、端口池 |
| 配置状态 | `GET /api/v1/config/status` | 配置存储状态 |

---

## 🔌 API 权限说明

### **无需认证**（开放调用）

✅ **服务器管理 API**
- `/api/v1/servers`
- `/api/v1/servers/{id}/status`
- `/api/v1/servers/{id}/start`
- `/api/v1/servers/{id}/stop`
- `/api/v1/servers/{id}/restart`
- `/api/v1/servers/start-all`
- `/api/v1/servers/stop-all`
- `/api/v1/servers/port-configs`
- `/api/v1/servers/{id}/port-config`

✅ **系统监控 API**
- `/api/v1/system`
- `/api/v1/system/resources`
- `/health`

✅ **用途**：
- 工作流自动化（n8n、Zapier）
- CI/CD 集成
- 监控系统集成
- API 调用工具

### **需要认证**（管理功能）

🔒 **Dashboard 和配置管理**
- `/dashboard` - 管理控制台
- `/api/v1/config/*` - 配置管理
- `/api/v1/auth/*` - 认证相关

---

## 📁 项目结构

```
MCP_Server_Brose/
├── main.py                     # 🚀 主入口
├── config/                     # ⚙️ 配置管理
│   ├── settings.py             # 系统配置
│   ├── port_config.py          # 端口配置
│   ├── servers.json            # 服务器配置（持久化）
│   ├── ports.json              # 端口配置（持久化）
│   ├── settings.json           # 系统设置（持久化）
│   └── backups/                # 配置备份
├── mcp_servers/                # 🧩 MCP 服务器模块
│   └── pdf_extractor/          # PDF 提取器
├── utils/                      # 🛠️ 工具函数
│   ├── process_manager.py      # 进程管理器
│   ├── port_allocator.py       # 端口分配器
│   ├── config_manager.py       # 配置管理器（新增）
│   ├── logger.py               # 日志系统
│   ├── security.py             # 安全工具（JWT、密码哈希）
│   └── auth.py                 # 认证 API
├── api/                        # 📡 API 路由
│   ├── system.py               # 系统监控 API
│   └── config.py               # 配置管理 API
├── middleware/                 # 🔌 中间件
│   └── proxy_middleware.py     # 请求转发中间件
├── dashboard/                  # 🎨 Dashboard 界面
│   └── index.html              # 可视化控制台
├── scripts/                    # 🔧 工具脚本
│   ├── start_safe.sh           # 安全启动脚本
│   └── stop.sh                 # 停止脚本
├── tests/                      # 🧪 单元测试
├── docs/                       # 📚 文档中心
├── logs/                       # 📋 日志目录
└── requirements.txt            # 📦 依赖管理
```

---

## 🧪 测试

### **运行单元测试**

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

### **测试配置持久化**

```bash
# 测试配置管理功能
python test_config_persistence.py
```

---

## 📚 文档中心

### 🚀 **快速开始**
- **[配置持久化指南](docs/CONFIG_PERSISTENCE.md)** - 配置存储和备份
- **[快速开始](docs/QUICK_START.md)** - 5 分钟快速上手
- **[启动指南](docs/STARTUP_GUIDE.md)** - 详细启动说明

### 🔧 **功能指南**
- **[端口管理](docs/PORT_MANAGEMENT.md)** - 端口配置完全指南
- **[N8N 集成](docs/N8N_INTEGRATION.md)** - 工作流集成指南
- **[故障排除](docs/TROUBLESHOOTING.md)** - 常见问题解决

### 🏗️ **架构理解**
- **[架构详解](docs/ARCHITECTURE.md)** - 系统架构和设计
- **[项目结构](docs/PROJECT_STRUCTURE.md)** - 目录组织

### 📋 **更新日志**
- **[Dashboard 功能完成报告](DASHBOARD_FEATURES_COMPLETED.md)** - 新功能详情
- **[改进完成报告](IMPROVEMENT_COMPLETED.md)** - 之前的功能改进

---

## 🎯 使用场景

### **1. 开发环境**
```bash
# 快速启动开发服务器
bash start_safe.sh

# Dashboard 管理
http://localhost:51234/dashboard
```

### **2. 工作流自动化**（n8n）
```javascript
// HTTP Request 节点
GET http://host.docker.internal:51234/api/v1/servers/statuses
认证: None（无需认证）

// 响应示例
{
  "pdf_extractor": {
    "status": "running",
    "port": 51238
  }
}
```

### **3. 生产部署**
```bash
# 1. 配置持久化
cp config/servers.json.example config/servers.json
vim config/servers.json  # 编辑配置

# 2. 修改密码
vim .env
# DASHBOARD_PASSWORD=your_secure_password

# 3. 设置 JWT 密钥
export JWT_SECRET_KEY="$(openssl rand -hex 32)"

# 4. 启动服务
bash start_safe.sh
```

---

## 🔐 安全建议

### **生产环境必做**

1. **修改默认密码**
```bash
# .env 文件
DASHBOARD_PASSWORD=your_secure_password
```

2. **设置 JWT 密钥**
```bash
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
```

3. **配置 CORS**
```bash
# .env 文件
CORS_ORIGINS=https://yourdomain.com
```

4. **启用日志轮转**
```bash
# 已自动启用（10MB 轮转，保留 5 个备份）
```

---

## 🛠️ 项目管理

### **核心维护者**
- **Jimmy** - 项目架构和开发

### **技术栈**
- **后端**: FastAPI + Python 3.12
- **前端**: Vanilla JavaScript + HTML5
- **认证**: JWT Token (PyJWT)
- **日志**: Python logging + RotatingFileHandler
- **测试**: pytest

### **依赖版本**
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
PyJWT>=2.8.0
psutil>=5.9.0
```

---

## 🚀 下一步计划

- [ ] **Docker 支持** - 容器化部署
- [ ] **自动恢复** - 服务崩溃自动重启
- [ ] **日志聚合** - 集中式日志查询
- [ ] **插件系统** - 动态加载服务器
- [ ] **集群模式** - 多节点部署

---

## 🆘 故障排除

### **问题：无法启动**
```bash
# 检查端口占用
lsof -ti:51234 | xargs kill -9

# 重新启动
bash start_safe.sh
```

### **问题：配置丢失**
```bash
# 配置已持久化，检查文件
ls -la config/

# 恢复备份
ls config/backups/
```

### **问题：API 返回 401**
```bash
# Dashboard 需要登录，直接访问 API 不会 401
# 如果 API 返回 401，检查代码是否重新部署
```

更多问题？查看 [故障排除指南](docs/TROUBLESHOOTING.md)

---

## 📄 许可证

MIT License

---

## 🎉 贡献

欢迎提交 Issue 和 Pull Request！

---

**📚 完整文档**: [docs/README.md](docs/README.md)  
**🐛 问题反馈**: [GitHub Issues](../../issues)  
**💡 功能建议**: [GitHub Discussions](../../discussions)
