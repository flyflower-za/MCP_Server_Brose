"""
全局配置管理
"""
import os
from pathlib import Path
from typing import Dict, Any

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    # 加载项目根目录的.env文件
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # 如果没有安装python-dotenv，忽略
    pass


class Settings:
    """全局配置类"""

    # 项目根目录
    BASE_DIR = Path(__file__).parent.parent

    # 服务器配置 - 优先使用.env文件中的配置
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MCP_PORT", "8000"))
    DEBUG: bool = os.getenv("MCP_DEBUG", "False").lower() == "true"

    # API配置
    API_PREFIX: str = "/api/v1"
    TITLE: str = "MCP Servers Hub"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "统一的MCP服务器管理系统"

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOG_DIR / "mcp_server.log"

    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # 超时配置
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # SSL配置
    SSL_VERIFY: bool = os.getenv("SSL_VERIFY", "False").lower() == "false"

    # 进程管理配置
    PROCESS_BASE_PORT: int = int(os.getenv("PROCESS_BASE_PORT", "51235"))  # 服务器进程起始端口
    PROCESS_MAX_RESTART: int = int(os.getenv("PROCESS_MAX_RESTART", "3"))  # 最大自动重启次数
    PROCESS_HEALTH_CHECK_INTERVAL: int = int(os.getenv("PROCESS_HEALTH_CHECK_INTERVAL", "30"))  # 健康检查间隔(秒)
    PROCESS_AUTO_RESTART: bool = os.getenv("PROCESS_AUTO_RESTART", "True").lower() == "true"  # 自动重启故障进程
    PROCESS_START_TIMEOUT: int = int(os.getenv("PROCESS_START_TIMEOUT", "10"))  # 进程启动超时(秒)
    PROCESS_STOP_TIMEOUT: int = int(os.getenv("PROCESS_STOP_TIMEOUT", "10"))  # 进程停止超时(秒)

    @classmethod
    def setup(cls):
        """初始化配置"""
        # 创建必要的目录
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

        return cls


# 全局配置实例
settings = Settings.setup()


# MCP服务器配置
MCP_SERVERS_CONFIG: Dict[str, Dict[str, Any]] = {
    "pdf_extractor": {
        "name": "PDF Extractor",
        "description": "Get PDF content from URLs",
        "enabled": True,
        "version": "1.0.0",
        "module": "mcp_servers.pdf_extractor.server",
        "prefix": "/pdf",
        "tags": ["pdf", "extractor", "document"]
    },
    # 可以在这里添加更多的MCP服务器
    # "web_scraper": {
    #     "name": "Web Scraper",
    #     "description": "Get content from websites",
    #     "enabled": False,
    #     "version": "1.0.0",
    #     "module": "mcp_servers.web_scraper.server",
    #     "prefix": "/scraper",
    #     "tags": ["web", "scraper", "html"]
    # },
}


def get_enabled_servers() -> Dict[str, Dict[str, Any]]:
    """获取已启用的MCP服务器"""
    return {
        server_id: config
        for server_id, config in MCP_SERVERS_CONFIG.items()
        if config.get("enabled", True)
    }


def get_server_config(server_id: str) -> Dict[str, Any]:
    """获取特定服务器的配置"""
    return MCP_SERVERS_CONFIG.get(server_id, {})
