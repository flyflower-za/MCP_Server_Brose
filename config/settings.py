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
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))  # 单个日志文件最大10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))  # 保留5个备份文件
    LOG_KEEP_DAYS: int = int(os.getenv("LOG_KEEP_DAYS", "7"))  # 清理7天前的日志

    # CORS配置（生产环境应该限制允许的来源）
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    CORS_ALLOW_METHODS: list = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
    CORS_ALLOW_HEADERS: list = os.getenv("CORS_ALLOW_HEADERS", "Content-Type,Authorization").split(",")
    CORS_MAX_AGE: int = int(os.getenv("CORS_MAX_AGE", "3600"))  # 1小时

    # 超时配置
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "120"))

    # SSL配置
    SSL_VERIFY: bool = os.getenv("SSL_VERIFY", "False").lower() == "false"

    # 进程管理配置
    # PROCESS_BASE_PORT 默认为 MCP_PORT + 1，可单独配置覆盖
    _mcp_port = int(os.getenv("MCP_PORT", "8000"))
    PROCESS_BASE_PORT: int = int(os.getenv("PROCESS_BASE_PORT", str(_mcp_port + 1)))
    PROCESS_MAX_RESTART: int = int(os.getenv("PROCESS_MAX_RESTART", "3"))  # 最大自动重启次数
    PROCESS_HEALTH_CHECK_INTERVAL: int = int(os.getenv("PROCESS_HEALTH_CHECK_INTERVAL", "30"))  # 健康检查间隔(秒)
    PROCESS_AUTO_RESTART: bool = os.getenv("PROCESS_AUTO_RESTART", "True").lower() == "true"  # 自动重启故障进程
    PROCESS_START_TIMEOUT: int = int(os.getenv("PROCESS_START_TIMEOUT", "10"))  # 进程启动超时(秒)
    PROCESS_STOP_TIMEOUT: int = int(os.getenv("PROCESS_STOP_TIMEOUT", "10"))  # 进程停止超时(秒)

    # Dashboard 安全配置
    DASHBOARD_USERNAME: str = os.getenv("DASHBOARD_USERNAME", "admin")
    DASHBOARD_PASSWORD: str = os.getenv("DASHBOARD_PASSWORD", "brose123")  # 建议在.env中修改
    DASHBOARD_AUTH_ENABLED: bool = os.getenv("DASHBOARD_AUTH_ENABLED", "True").lower() == "true"  # 是否启用认证
    DASHBOARD_REFRESH_INTERVAL: int = int(os.getenv("DASHBOARD_REFRESH_INTERVAL", "30"))  # 自动刷新间隔(秒)

    # JWT Token 配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 1440)  # 24小时

    # API Key配置（永久有效，用于插件集成）
    API_KEY: str = os.getenv("API_KEY", "your-permanent-api-key-change-this")

    # MCP服务器模块启用配置（通过环境变量控制）
    ENABLE_PDF_EXTRACTOR: bool = os.getenv("ENABLE_PDF_EXTRACTOR", "True").lower() == "true"
    ENABLE_QRCODE_READER: bool = os.getenv("ENABLE_QRCODE_READER", "True").lower() == "true"
    ENABLE_PDF_SIGNATURE_VERIFIER: bool = os.getenv("ENABLE_PDF_SIGNATURE_VERIFIER", "False").lower() == "true"  # 默认禁用 - macOS兼容性问题

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
        "enabled": settings.ENABLE_PDF_EXTRACTOR,
        "version": "1.0.0",
        "module": "mcp_servers.pdf_extractor.server",
        "prefix": "/pdf",
        "tags": ["pdf", "extractor", "document"]
    },
    "qrcode_reader": {
        "name": "QR Code Reader",
        "description": "Extract content from QR codes in images",
        "enabled": settings.ENABLE_QRCODE_READER,
        "version": "1.0.0",
        "module": "mcp_servers.qrcode_reader.server",
        "prefix": "/qrcode",
        "tags": ["qrcode", "image", "reader", "barcode"]
    },
    "pdf_signature_verifier": {
        "name": "PDF Signature Verifier",
        "description": "Verify digital signatures in PDF files",
        "enabled": settings.ENABLE_PDF_SIGNATURE_VERIFIER,  # 通过环境变量控制，默认禁用
        "version": "1.0.0",
        "module": "mcp_servers.pdf_signature_verifier.server",
        "prefix": "/signature",
        "tags": ["pdf", "signature", "verification", "security"]
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
