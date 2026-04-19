# MCP服务器管理系统 - 项目结构

```
MCP_Server/
├── main.py                    # 主服务器入口
├── config/
│   ├── __init__.py
│   ├── settings.py           # 全局配置
│   └── mcp_config.yaml       # MCP服务器配置文件
├── mcp_servers/              # MCP服务器模块目录
│   ├── __init__.py
│   ├── pdf_extractor/        # PDF提取器服务
│   │   ├── __init__.py
│   │   ├── server.py         # 服务实现
│   │   └── models.py         # 数据模型
│   ├── web_scraper/          # 示例：网页抓取服务
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── models.py
│   └── data_processor/       # 示例：数据处理服务
│       ├── __init__.py
│       ├── server.py
│       └── models.py
├── utils/                    # 工具函数
│   ├── __init__.py
│   ├── http_helpers.py
│   └── logger.py
├── logs/                     # 日志目录
├── tests/                    # 测试文件
├── requirements.txt          # 统一依赖管理
├── start.sh                  # 启动脚本
├── client_example.py         # 客户端示例
└── README.md                 # 项目文档
```

## 核心特性

- ✅ 模块化设计，每个MCP服务独立开发
- ✅ 统一的路由管理，易于扩展
- ✅ 配置文件管理，启动/停用服务
- ✅ 统一的日志系统
- ✅ 统一的错误处理
- ✅ API版本控制
