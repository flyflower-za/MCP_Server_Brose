# MCP Servers Hub - 项目概述

本文档提供了MCP Servers Hub项目的完整概述，包括项目结构、架构分析和核心特性。

## 📋 目录

- [项目简介](#项目简介)
- [目录结构](#目录结构)
- [核心组件](#核心组件)
- [技术架构](#技术架构)
- [工作流程](#工作流程)
- [扩展开发](#扩展开发)

---

## 🎯 项目简介

### 项目定位
MCP Servers Hub是一个统一的、可扩展的MCP（Model Context Protocol）服务器管理系统，采用进程隔离架构，支持动态服务发现和管理。

### 核心特性
- 🚀 **进程隔离架构**: 每个MCP服务器运行在独立进程中
- 🔄 **动态端口管理**: 支持动态和固定端口分配
- 📊 **可视化Dashboard**: 实时监控和管理界面
- 🔐 **安全认证**: 支持Basic Auth和JWT Token
- ⚙️ **配置持久化**: 自动保存配置更改
- 🛡️ **错误恢复**: 自动重启故障进程

### 技术栈
- **后端框架**: FastAPI + Uvicorn
- **进程管理**: psutil + subprocess
- **前端**: 原生JavaScript + CSS
- **数据库**: JSON文件存储
- **日志**: Python logging模块

---

## 📂 目录结构

### 完整项目结构

```
MCP_Server_Brose/                    # 🎯 项目根目录
│
├── 📄 核心入口文件
├── main.py                          # 🚀 系统主入口
├── requirements.txt                 # 📦 Python依赖管理
├── .env                             # 🔐 环境配置文件
├── .env.example                     # 📋 配置文件示例
├── ecosystem.config.js              # 🔧 PM2进程管理配置
├── start_safe.sh                    # ▶️ 安全启动脚本
├── stop.sh                          # ⏹️ 停止脚本
├── client_example.py                # 💻 客户端示例
│
├── ⚙️ config/                       # 🔧 配置管理目录
│   ├── __init__.py                  # 配置模块初始化
│   ├── settings.py                  # 🔑 全局配置中心
│   ├── port_config.py               # 🔌 端口配置管理
│   └── mcp_config.yaml              # 📋 MCP服务器配置（可选）
│
├── 🧩 mcp_servers/                  # 📦 MCP服务器模块目录
│   ├── __init__.py                  # 服务器模块导出
│   ├── pdf_extractor/               # 📄 PDF提取器服务
│   │   ├── __init__.py              # 模块初始化
│   │   ├── server.py                # 服务实现和路由
│   │   └── models.py                # Pydantic数据模型
│   └── qrcode_reader/               # 📱 二维码识别服务
│       ├── __init__.py              # 模块初始化
│       ├── server.py                # 服务实现和路由
│       └── models.py                # Pydantic数据模型
│
├── 🛠️ utils/                        # 🔨 工具函数目录
│   ├── __init__.py                  # 工具模块初始化
│   ├── logger.py                    # 📋 统一日志管理
│   ├── http_helpers.py              # 🌐 HTTP请求辅助
│   ├── process_manager.py           # 🔄 进程管理器
│   └── security.py                  # 🔐 安全认证工具
│
├── 🌐 middleware/                   # 🛡️ 中间件目录
│   ├── __init__.py                  # 中间件模块初始化
│   └── proxy_middleware.py          # 🔄 请求转发中间件
│
├── 📡 api/                          # 🌐 API端点目录
│   ├── __init__.py                  # API模块初始化
│   ├── system.py                    # 🖥️ 系统监控API
│   ├── config.py                    # ⚙️ 配置管理API
│   └── auth.py                      # 🔐 认证API
│
├── 🔧 scripts/                      # 📜 脚本目录
│   ├── start.sh                     # ▶️ 标准启动脚本
│   ├── restart.sh                   # 🔄 重启脚本
│   ├── check_startup.sh             # 🔍 启动检查脚本
│   ├── create_mcp_server.py         # 🏗️ 服务器创建脚本
│   └── utils/                       # 🛠️ 工具脚本
│       ├── test_n8n_api.py          # 🧪 API测试脚本
│       └── test_n8n_connection.sh   # 🔗 连接测试脚本
│
├── 🧪 tests/                        # ⚗️ 测试目录
│   ├── __init__.py                  # 测试模块初始化
│   ├── test_main.py                 # 主程序测试
│   └── test_config_persistence.py   # 配置持久化测试
│
├── 📋 logs/                         # 📝 日志文件目录
│   ├── mcp_server.log               # 系统运行日志
│   ├── mcp_server.log.1             # 日志轮转备份
│   └── ...                          # 其他日志文件
│
├── 🎨 dashboard/                    # 🖥️ Dashboard目录
│   └── index.html                   # 📊 可视化管理界面
│
├── 📚 docs/                         # 📖 文档目录
│   ├── README.md                    # 项目说明
│   ├── GETTING_STARTED.md           # 快速开始
│   ├── PORT_GUIDE.md                # 端口管理指南
│   ├── API_REFERENCE.md             # API参考手册
│   ├── ARCHITECTURE.md              # 架构详解
│   ├── PROJECT_OVERVIEW.md          # 项目概述（本文档）
│   ├── TROUBLESHOOTING.md           # 故障排除
│   └── ...                          # 其他文档
│
├── 📦 examples/                     # 💡 示例目录
│   └── basic_usage/                 # 基础使用示例
│
├── 🗄️ .git/                        # 📦 Git版本控制
├── 🚫 .gitignore                    # 🔞 Git忽略配置
└── 🔐 .claude/                      # 🤖 Claude配置目录
```

---

## 🧩 核心组件

### 1. 主入口系统 ([main.py](../main.py))

#### 功能职责
- **API网关**: FastAPI应用，统一入口
- **进程管理**: 启动和管理所有MCP服务器进程
- **请求路由**: 通过中间件转发请求到对应服务
- **监控管理**: 提供系统监控和管理API

#### 主要端点
```python
# 系统端点
GET  /                           # 根路径重定向
GET  /dashboard                  # Dashboard界面
GET  /health                     # 健康检查
GET  /docs                       # API文档

# 管理API
GET  /api/v1/servers             # 服务器列表
POST /api/v1/servers/{id}/start  # 启动服务器
POST /api/v1/servers/{id}/stop   # 停止服务器
POST /api/v1/servers/{id}/restart # 重启服务器
```

### 2. 配置管理系统 ([config/](../config))

#### 全局配置 ([settings.py](../config/settings.py))
```python
class Settings:
    # 基础配置
    HOST: str = "0.0.0.0"
    PORT: int = 51234
    DEBUG: bool = False

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = BASE_DIR / "logs"

    # 进程管理
    PROCESS_BASE_PORT: int = 51235
    PROCESS_AUTO_RESTART: bool = True
    PROCESS_MAX_RESTART: int = 3

    # 安全配置
    DASHBOARD_USERNAME: str = "admin"
    DASHBOARD_PASSWORD: str = "brose123"
    JWT_SECRET_KEY: str = ""

# MCP服务器配置
MCP_SERVERS_CONFIG = {
    "pdf_extractor": {
        "name": "PDF Extractor",
        "description": "Get PDF content from URLs",
        "enabled": True,
        "module": "mcp_servers.pdf_extractor.server",
        "prefix": "/pdf"
    },
    "qrcode_reader": {
        "name": "QR Code Reader",
        "description": "Extract content from QR codes",
        "enabled": True,
        "module": "mcp_servers.qrcode_reader.server",
        "prefix": "/qrcode"
    }
}
```

#### 端口配置 ([port_config.py](../config/port_config.py))
- **功能**: 管理服务器固定端口配置
- **存储**: JSON文件持久化
- **API**: 提供端口增删查查接口

### 3. MCP服务器模块 ([mcp_servers/](../mcp_servers))

#### 模块结构
```python
# 标准MCP服务器结构
mcp_servers/
├── server_name/
│   ├── __init__.py          # 导出router和get_info
│   ├── server.py            # 实现服务逻辑
│   └── models.py            # 数据模型定义
```

#### 服务器示例 ([pdf_extractor](../mcp_servers/pdf_extractor))
```python
# server.py 核心结构
from fastapi import APIRouter

router = APIRouter(tags=["PDF Extractor"])

@router.post("/extract")
async def extract_pdf(request: PDFExtractRequest):
    """PDF提取端点"""
    result = extract_pdf_from_url(request.url)
    return result

def get_info():
    """返回服务器信息"""
    return {
        "name": "PDF Extractor",
        "version": "1.0.0",
        "endpoints": [...]
    }
```

### 4. 工具函数库 ([utils/](../utils))

#### 进程管理器 ([process_manager.py](../utils/process_manager.py))
```python
class ProcessManager:
    def start_server(self, server_id, config):
        """启动服务器进程"""
        # 分配端口
        # 创建子进程
        # 监控健康状态

    def stop_server(self, server_id):
        """停止服务器进程"""
        # 发送终止信号
        # 等待进程结束
        # 清理资源
```

#### 日志管理 ([logger.py](../utils/logger.py))
```python
# 统一日志配置
- 日志轮转: 10MB/文件
- 备份数量: 5个
- 日志级别: INFO/WARNING/ERROR
- 输出格式: 时间-级别-消息
```

#### 安全工具 ([security.py](../utils/security.py))
```python
class TokenManager:
    def create_token(self, username):
        """生成JWT Token"""
        # 24小时有效期
        # HS256算法

    def verify_token(self, token):
        """验证Token有效性"""
        # 检查签名
        # 检查过期时间
```

### 5. 中间件系统 ([middleware/](../middleware))

#### 请求转发中间件 ([proxy_middleware.py](../middleware/proxy_middleware.py))
```python
class ProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 1. 检查是否需要转发
        # 2. 解析目标服务器
        # 3. 移除路径前缀
        # 4. 转发请求到服务器
        # 5. 返回响应
```

#### 转发逻辑
```
客户端请求: /pdf/extract
  ↓
解析前缀: /pdf → pdf_extractor
  ↓
移除前缀: /extract
  ↓
转发到: http://127.0.0.1:51235/extract
  ↓
返回结果
```

### 6. API系统 ([api/](../api))

#### 系统监控API ([system.py](../api/system.py))
```python
@router.get("/resources")
async def get_system_resources():
    """获取系统资源使用情况"""
    return {
        "hub": {"cpu_percent": 5.2, "memory_mb": 256},
        "processes": {...},
        "port_pool": {...}
    }
```

#### 配置管理API ([config.py](../api/config.py))
```python
@router.get("/servers")
async def get_servers_config():
    """获取所有服务器配置"""

@router.post("/servers/{server_id}")
async def add_server(server_id: str, config: ServerConfig):
    """添加新服务器"""
```

### 7. Dashboard ([dashboard/](../dashboard))

#### 技术栈
- **纯前端**: HTML + CSS + JavaScript
- **无框架**: 原生JS实现，减少依赖
- **实时更新**: 15秒自动刷新
- **响应式**: 支持移动端访问

#### 主要功能
- 📊 **服务器监控**: 实时状态显示
- 🎛️ **服务控制**: 启动/停止/重启
- 🔌 **端口配置**: 固定端口管理
- 📋 **操作日志**: 实时操作记录
- 🧪 **功能测试**: PDF提取、二维码识别

---

## 🏗️ 技术架构

### 架构设计原则

#### 1. 进程隔离
```
┌─────────────────────────────────────┐
│         API Gateway (main.py)        │
│              Port: 51234             │
└─────────────────────────────────────┘
              ↓ ↓ ↓
┌─────────────┼─────────────┬──────────────┐
│             │             │              │
┌─────────────┴───┐  ┌──────┴──────┐  ┌───┴─────────┐
│ PDF Extractor  │  │ QR Reader   │  │ Future...   │
│ Port: 51235    │  │ Port: 51236  │  │ Port: 51237+│
└────────────────┘  └─────────────┘  └─────────────┘
```

#### 2. 分层架构
```
表示层 (Dashboard)
    ↓
应用层 (API Routes)
    ↓
业务层 (Process Manager)
    ↓
数据层 (JSON Config)
    ↓
执行层 (MCP Server Processes)
```

#### 3. 模块化设计
- **低耦合**: 各模块独立运行
- **高内聚**: 相关功能集中管理
- **可扩展**: 新增服务器无需修改核心
- **可维护**: 统一的代码结构

### 数据流设计

#### 请求处理流程
```
用户请求
  ↓
[认证中间件]
  ↓
[转发中间件] → 解析服务器ID
  ↓
[API网关] → 转发到目标服务器
  ↓
[MCP服务器] → 处理业务逻辑
  ↓
[响应返回] → 网关聚合响应
  ↓
用户接收结果
```

#### 配置管理流程
```
配置更改
  ↓
[内存更新] → 实时生效
  ↓
[文件持久化] → 永久保存
  ↓
[进程重启] → 应用新配置
  ↓
[状态同步] → Dashboard更新
```

---

## 🔄 工作流程

### 系统启动流程

#### 1. 环境初始化
```bash
# 加载环境变量
python -c "from dotenv import load_dotenv; load_dotenv()"

# 创建必要目录
mkdir -p logs config

# 检查配置文件
python -c "from config import settings; print(settings.MCP_PORT)"
```

#### 2. 进程启动
```python
# main.py 启动流程
1. 创建FastAPI应用
2. 配置CORS中间件
3. 添加转发中间件
4. 加载路由系统
5. 启动MCP服务器进程
6. 启动Uvicorn服务器
```

#### 3. 服务器管理
```python
# 进程管理器启动流程
for server_id, config in enabled_servers:
    # 分配端口
    port = allocate_port(server_id)

    # 启动进程
    process = subprocess.Popen([
        "python", "-m", config["module"]
    ], env={**os.environ, "PORT": str(port)})

    # 监控健康
    monitor_process(process)
```

### 请求处理流程

#### API请求
```
1. 客户端请求 → http://localhost:51234/pdf/extract
2. 认证检查 → JWT Token验证
3. 路由解析 → 识别目标服务器
4. 请求转发 → http://localhost:51235/extract
5. 业务处理 → PDF提取逻辑
6. 响应返回 → JSON格式结果
```

#### Dashboard请求
```
1. 浏览器访问 → http://localhost:51234/dashboard
2. 静态文件服务 → index.html
3. JavaScript加载 → 初始化界面
4. API轮询 → 15秒刷新状态
5. 用户交互 → 发送控制请求
6. 实时更新 → DOM更新显示
```

---

## 🔧 扩展开发

### 添加新的MCP服务器

#### 1. 创建服务器模块
```bash
# 创建目录结构
mkdir -p mcp_servers/my_service/
touch mcp_servers/my_service/__init__.py
touch mcp_servers/my_service/server.py
touch mcp_servers/my_service/models.py
```

#### 2. 实现服务逻辑
```python
# mcp_servers/my_service/server.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["My Service"])

class MyRequest(BaseModel):
    data: str

@router.post("/process")
async def process_data(request: MyRequest):
    """处理数据"""
    result = {"processed": request.data}
    return result

def get_info():
    """返回服务器信息"""
    return {
        "name": "My Service",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/my_service/process", "method": "POST"}
        ]
    }
```

#### 3. 注册到系统配置
```python
# config/settings.py
MCP_SERVERS_CONFIG = {
    # ... 现有服务器
    "my_service": {
        "name": "My Service",
        "description": "My custom service",
        "enabled": True,
        "version": "1.0.0",
        "module": "mcp_servers.my_service.server",
        "prefix": "/my_service",
        "tags": ["custom", "service"]
    }
}
```

#### 4. 测试新服务器
```bash
# 重启系统
./start_safe.sh

# 测试新服务
curl -X POST http://localhost:51234/my_service/process \
  -H "Content-Type: application/json" \
  -d '{"data": "test"}'
```

### 自定义中间件

#### 添加认证中间件
```python
# middleware/custom_auth.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CustomAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 自定义认证逻辑
        token = request.headers.get("X-Custom-Token")
        if not self.validate_token(token):
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized"}
            )
        return await call_next(request)

# 在main.py中添加
app.add_middleware(CustomAuthMiddleware)
```

---

## 📊 性能优化

### 资源管理

#### 进程资源限制
```python
# 限制进程资源使用
import resource

def set_resource_limits():
    """设置进程资源限制"""
    # 限制内存使用: 512MB
    resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, -1))

    # 限制CPU时间: 60秒
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
```

#### 连接池优化
```python
# httpx异步连接池
import httpx

client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    )
)
```

### 缓存策略

#### 配置缓存
```python
# 缓存服务器配置
from functools import lru_cache

@lru_cache(maxsize=128)
def get_server_config(server_id: str):
    """获取服务器配置（带缓存）"""
    return load_config_from_file(server_id)
```

#### 响应缓存
```python
# API响应缓存
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

FastAPICache.init(RedisBackend(redis), prefix="mcp_api")
```

---

## 🛡️ 安全考虑

### 认证与授权

#### JWT Token认证
```python
# 生成Token
token = create_access_token(username, expires_delta=timedelta(hours=24))

# 验证Token
payload = jwt.decode(token, secret_key, algorithms=["HS256"])
```

#### 权限控制
```python
# 基于角色的访问控制
ROLES = {
    "admin": ["read", "write", "delete"],
    "user": ["read"]
}

def check_permission(user_role: str, required_permission: str):
    """检查用户权限"""
    return required_permission in ROLES.get(user_role, [])
```

### 数据安全

#### 敏感数据加密
```python
# 配置文件加密
from cryptography.fernet import Fernet

def encrypt_config(data: str) -> bytes:
    """加密配置数据"""
    key = load_encryption_key()
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())
```

#### 日志脱敏
```python
# 日志中隐藏敏感信息
import re

def sanitize_log(message: str) -> str:
    """脱敏日志信息"""
    # 隐藏密码
    message = re.sub(r'password=["\']([^"\']+)["\']', 'password="***"', message)
    # 隐藏Token
    message = re.sub(r'token=["\']([^"\']+)["\']', 'token="***"', message)
    return message
```

---

## 📚 相关文档

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 快速开始指南
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 详细架构说明
- **[API_REFERENCE.md](API_REFERENCE.md)** - API参考手册
- **[PORT_GUIDE.md](PORT_GUIDE.md)** - 端口管理指南
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排除

---

## 🎯 开发路线图

### 当前版本 (v1.0.0)
- ✅ 基础进程隔离架构
- ✅ Dashboard可视化界面
- ✅ PDF提取器服务
- ✅ 二维码识别服务
- ✅ 配置持久化
- ✅ JWT认证

### 未来计划 (v1.1.0)
- 🔲 更多MCP服务器集成
- 🔲 性能监控面板
- 🔲 告警系统
- 🔲 Docker容器化
- 🔲 CI/CD流水线

---

**💡 提示**: 这个项目采用模块化设计，你可以轻松扩展新的MCP服务器。参考现有的服务器实现来创建你自己的服务！

**🔗 快速开始**: 查看 [GETTING_STARTED.md](GETTING_STARTED.md) 立即开始使用！
