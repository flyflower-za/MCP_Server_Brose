# MCP服务器管理系统

统一的MCP服务器管理系统，支持多个MCP服务器的模块化开发和管理。

> 📚 **完整文档请查看：** [docs/README.md](docs/README.md)

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置端口

```bash
# 编辑 .env 文件修改端口
vim .env
# MCP_PORT=8000  # 修改为你想要的端口
```

### 3. 启动系统

```bash
# 使用启动脚本
./start.sh

# 或直接运行
python main.py
```

### 4. 检查状态

```bash
# 检查服务器状态（自动检测端口配置）
./check_startup.sh
```

### 5. 访问服务

根据你在 `.env` 中配置的端口访问：
- 主页: http://localhost:8000 (或你配置的端口)
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 📖 详细文档

所有详细文档都已整理在 [docs/](docs/README.md) 目录中：

### 🚀 **新手必读**
- **[快速配置](docs/QUICK_START.md)** - 端口配置快速指南
- **[启动指南](docs/STARTUP_GUIDE.md)** - 详细的启动步骤和故障排除
- **[端口管理](docs/PORT_MANAGEMENT.md)** - 端口配置和管理完全指南

### 🏗️ **系统理解**
- **[架构详解](docs/ARCHITECTURE.md)** - 系统架构和设计原理
- **[项目结构](docs/PROJECT_STRUCTURE.md)** - 目录结构和文件组织
- **[项目分析](docs/PROJECT_ANALYSIS.md)** - 深入的技术分析

## 🔌 当前可用服务

### PDF提取器 (`/pdf`)

从URL提取PDF文本内容

**端点:**
- `POST /extract` - 提取单个PDF
- `POST /extract/batch` - 批量提取PDF

**使用示例:**
```python
import requests

response = requests.post("http://localhost:8000/extract", json={
    "url": "https://example.com/document.pdf",
    "include_metadata": True
})

result = response.json()
print(result["content"])
```

## 🔧 添加新的MCP服务器

### 快速方法（推荐）

```bash
# 创建新的MCP服务器
python scripts/create_mcp_server.py my_service "服务描述"
```

### 手动方法

1. 创建服务模块目录和文件
2. 在 `config/settings.py` 中注册服务器
3. 重启系统

详细步骤请参考 [项目分析文档](docs/PROJECT_ANALYSIS.md)。

## 🛠️ 项目管理

### 核心文件
- `main.py` - 系统主入口
- `config/settings.py` - 全局配置
- `requirements.txt` - 依赖管理
- `start.sh` - 启动脚本

### 目录结构
```
MCP_Server/
├── main.py                    # 🚀 主入口
├── config/                    # ⚙️ 配置管理
├── mcp_servers/              # 🧩 MCP服务器模块
├── utils/                    # 🛠️ 工具函数
├── scripts/                  # 🔧 开发脚本
├── docs/                     # 📚 文档中心
├── logs/                     # 📋 日志目录
└── requirements.txt          # 📦 依赖管理
```

## 🧪 测试

```bash
# 检查系统状态
./check_startup.sh

# 使用客户端测试
python client_example.py

# 查看API文档
open http://localhost:8000/docs
```

## 📚 文档中心

📖 **所有文档都在 [docs/](docs/README.md) 目录中：**

- [启动指南](docs/STARTUP_GUIDE.md) - 详细启动说明
- [架构文档](docs/ARCHITECTURE.md) - 系统架构详解
- [端口管理](docs/PORT_MANAGEMENT.md) - 端口配置指南
- [项目分析](docs/PROJECT_ANALYSIS.md) - 技术深度分析

## 🔮 开发计划

- [ ] 添加更多MCP服务器模板
- [ ] 实现服务监控面板
- [ ] 添加配置热重载
- [ ] 实现服务间通信

## 📄 许可证

MIT License

---

**📚 需要更多信息？** 查看 [docs/README.md](docs/README.md) 获取完整文档！
