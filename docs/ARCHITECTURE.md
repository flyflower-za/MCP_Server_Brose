# MCP服务器管理系统 - 架构说明

## 🎯 项目概述

这是一个模块化的MCP服务器管理系统，支持动态加载和管理多个MCP服务器模块。

## 📂 核心目录结构

```
MCP_Server/
├── main.py                    # 🚀 主入口，负责启动和管理所有MCP服务器
├── config/                    # ⚙️ 配置管理
│   ├── settings.py           # 全局配置和MCP服务器注册
│   └── __init__.py
├── mcp_servers/              # 🧩 MCP服务器模块目录
│   ├── pdf_extractor/        # 📄 PDF提取器服务
│   │   ├── server.py         # 服务实现和路由定义
│   │   ├── models.py         # Pydantic数据模型
│   │   └── __init__.py
│   └── __init__.py
├── utils/                    # 🛠️ 通用工具函数
│   ├── logger.py            # 统一日志管理
│   ├── http_helpers.py      # HTTP请求辅助函数
│   └── __init__.py
├── logs/                     # 📋 日志文件目录
├── scripts/                  # 🔧 开发脚本
│   └── create_mcp_server.py # 创建新MCP服务器的脚本
└── requirements.txt          # 📦 Python依赖
```

## 🔌 插件式架构

### 如何添加新的MCP服务器

#### 方法1: 使用创建脚本（推荐）

```bash
python scripts/create_mcp_server.py my_service "我的服务描述"
```

这将自动创建：
- `mcp_servers/my_service/` 目录
- `__init__.py`, `server.py`, `models.py` 文件
- 更新 `config/settings.py` 配置

#### 方法2: 手动创建

1. **创建模块目录**
```bash
mkdir -p mcp_servers/my_service
```

2. **创建数据模型** (`mcp_servers/my_service/models.py`)
```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    input_data: str

class MyResponse(BaseModel):
    result: str
```

3. **创建服务实现** (`mcp_servers/my_service/server.py`)
```python
from fastapi import APIRouter
from .models import MyRequest, MyResponse

router = APIRouter(tags=["My Service"])

@router.post("/process", response_model=MyResponse)
async def process(request: MyRequest):
    return MyResponse(result="success")

def get_info():
    return {"name": "My Service", "version": "1.0.0"}
```

4. **注册服务器** (编辑 `config/settings.py`)
```python
MCP_SERVERS_CONFIG = {
    "my_service": {
        "name": "My Service",
        "description": "服务描述",
        "enabled": True,
        "version": "1.0.0",
        "module": "mcp_servers.my_service.server",
        "prefix": "/my-service",
        "tags": ["my", "service"]
    }
}
```

## 🏗️ 工作原理

### 启动流程

1. **main.py** 启动FastAPI应用
2. 从 `config/settings.py` 读取启用的服务器配置
3. 动态导入每个服务器的模块
4. 调用 `load_mcp_server()` 注册路由
5. 启动HTTP服务器

### 动态加载机制

```python
# 在main.py中
def load_mcp_server(server_id, server_config):
    # 动态导入模块
    module = importlib.import_module(server_config["module"])

    # 获取router和get_info函数
    router = getattr(module, 'router', None)
    info_func = getattr(module, 'get_info', None)

    # 注册路由到主应用
    app.include_router(router)
```

## 🔧 配置管理

### 全局配置 (`config/settings.py`)

```python
class Settings:
    HOST = "0.0.0.0"      # 服务器地址
    PORT = 8000           # 服务器端口
    DEBUG = False         # 调试模式
    LOG_LEVEL = "INFO"    # 日志级别
```

### 服务器配置

```python
MCP_SERVERS_CONFIG = {
    "server_id": {
        "name": "显示名称",
        "description": "服务描述",
        "enabled": True,              # 是否启用
        "version": "1.0.0",
        "module": "python模块路径",
        "prefix": "/路由前缀",
        "tags": ["标签1", "标签2"]
    }
}
```

## 🛠️ 工具函数

### 日志系统 (`utils/logger.py`)

```python
from utils.logger import logger

logger.info("信息日志")
logger.error("错误日志")
logger.debug("调试日志")
```

### HTTP辅助 (`utils/http_helpers.py`)

```python
from utils.http_helpers import fetch_url

response = fetch_url(url, timeout=30, verify_ssl=False)
content = response.content
```

## 📊 API端点结构

### 系统端点
- `GET /` - 系统信息
- `GET /health` - 健康检查
- `GET /servers` - 服务器列表
- `GET /docs` - API文档

### 服务端点 (PDF提取器示例)
- `POST /extract` - 提取单个PDF
- `POST /extract/batch` - 批量提取PDF

## 🚀 部署建议

### 开发环境
```bash
python main.py
```

### 生产环境
```bash
# 使用gunicorn
gunicorn main:app --workers 4 --bind 0.0.0.0:8000

# 使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🧪 测试

### 测试单个服务
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/doc.pdf"}'
```

### 查看系统状态
```bash
curl http://localhost:8000/
curl http://localhost:8000/servers
```

## 📝 最佳实践

1. **模块隔离** - 每个MCP服务器完全独立，互不依赖
2. **配置驱动** - 通过 `enabled: False` 轻松禁用服务
3. **统一日志** - 使用 `utils/logger` 记录所有操作
4. **错误处理** - 在服务端点中捕获异常并返回统一格式
5. **文档化** - 每个服务都有完整的docstring和类型提示

## 🔮 未来扩展

- [ ] 添加WebSocket支持
- [ ] 服务监控和统计
- [ ] 配置热重载
- [ ] 服务间通信
- [ ] 认证和授权系统
