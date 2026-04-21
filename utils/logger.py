"""
日志管理工具
支持日志轮转和文件大小限制
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from config.settings import settings


def setup_logger(name: str = "mcp_hub") -> logging.Logger:
    """
    设置并返回日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（支持轮转）
    if settings.LOG_FILE:
        # 确保日志目录存在
        settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_rotating_file_handler(log_file: Path, max_bytes: int = 10*1024*1024, backup_count: int = 5) -> RotatingFileHandler:
    """
    获取支持轮转的文件处理器

    Args:
        log_file: 日志文件路径
        max_bytes: 单个日志文件最大字节数（默认 10MB）
        backup_count: 保留的备份文件数量（默认 5）

    Returns:
        RotatingFileHandler 实例
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )

    return handler


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器（便捷函数）

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)


def log_rotation_size_check(log_file: Path, max_size_mb: int = 10) -> bool:
    """
    检查日志文件是否需要轮转

    Args:
        log_file: 日志文件路径
        max_size_mb: 最大文件大小（MB）

    Returns:
        是否需要轮转
    """
    if not log_file.exists():
        return False

    size_bytes = log_file.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    return size_mb >= max_size_mb


# 全局日志实例
logger = setup_logger()
