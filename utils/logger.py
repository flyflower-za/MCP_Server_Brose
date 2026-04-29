"""
日志管理工具
支持日志轮转、结构化日志、文件大小限制
"""
import logging
import sys
import json
from pathlib import Path
from typing import Any, Dict
from logging.handlers import RotatingFileHandler
from datetime import datetime

from config.settings import settings


def setup_logger(name: str = "mcp_hub", structured: bool = False) -> logging.Logger:
    """
    设置并返回日志记录器

    Args:
        name: 日志记录器名称
        structured: 是否使用结构化日志格式

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 创建格式化器
    if structured:
        formatter = StructuredFormatter()
    else:
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
            maxBytes=settings.LOG_MAX_BYTES,  # 从配置读取
            backupCount=settings.LOG_BACKUP_COUNT,  # 从配置读取
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器 - JSON 格式"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为 JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, 'extra_data'):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class EnhancedLogger:
    """增强的日志记录器，支持结构化日志和额外字段"""

    def __init__(self, name: str = "mcp_hub", structured: bool = False):
        """初始化增强日志记录器"""
        self.logger = setup_logger(name, structured)
        self.structured = structured

    def log_with_extra(self, level: str, message: str, **kwargs):
        """记录包含额外字段的日志"""
        extra_data = kwargs if self.structured else {}
        if extra_data:
            # 将额外数据添加到日志记录
            log_func = getattr(self.logger, level.lower())
            # 创建适配的日志记录
            extra = {'extra_data': extra_data}
            log_func(message, extra=extra)
        else:
            log_func = getattr(self.logger, level.lower())
            log_func(message)

    def info(self, message: str, **kwargs):
        """INFO 级别日志"""
        self.log_with_extra('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """WARNING 级别日志"""
        self.log_with_extra('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """ERROR 级别日志"""
        self.log_with_extra('ERROR', message, **kwargs)

    def debug(self, message: str, **kwargs):
        """DEBUG 级别日志"""
        self.log_with_extra('DEBUG', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """CRITICAL 级别日志"""
        self.log_with_extra('CRITICAL', message, **kwargs)


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


def cleanup_old_logs(log_dir: Path, pattern: str = "*.log*", keep_days: int = 7) -> int:
    """
    清理旧的日志文件

    Args:
        log_dir: 日志目录
        pattern: 文件匹配模式
        keep_days: 保留天数

    Returns:
        删除的文件数量
    """
    import time
    from pathlib import Path

    if not log_dir.exists():
        return 0

    current_time = time.time()
    deleted_count = 0

    for log_file in log_dir.glob(pattern):
        # 检查文件修改时间
        file_mtime = log_file.stat().st_mtime
        file_age_days = (current_time - file_mtime) / (24 * 3600)

        if file_age_days > keep_days:
            try:
                log_file.unlink()
                deleted_count += 1
                logger.info(f"删除旧日志文件: {log_file.name}")
            except Exception as e:
                logger.error(f"删除日志文件失败 {log_file.name}: {e}")

    return deleted_count


def get_log_files_info(log_dir: Path, pattern: str = "*.log*") -> Dict[str, Any]:
    """
    获取日志文件信息

    Args:
        log_dir: 日志目录
        pattern: 文件匹配模式

    Returns:
        日志文件信息字典
    """
    if not log_dir.exists():
        return {"files": [], "total_size_mb": 0, "file_count": 0}

    files_info = []
    total_size = 0

    for log_file in sorted(log_dir.glob(pattern)):
        size_bytes = log_file.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

        files_info.append({
            "name": log_file.name,
            "size_mb": round(size_mb, 2),
            "modified_time": mtime.isoformat()
        })
        total_size += size_bytes

    return {
        "files": files_info,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "file_count": len(files_info)
    }


def set_log_level(logger_name: str, level: str) -> bool:
    """
    动态设置日志级别

    Args:
        logger_name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        是否设置成功
    """
    try:
        log = logging.getLogger(logger_name)
        log.setLevel(getattr(logging, level.upper()))
        return True
    except AttributeError:
        return False


def get_log_stats(logger_name: str = "mcp_hub") -> Dict[str, Any]:
    """
    获取日志统计信息

    Args:
        logger_name: 日志记录器名称

    Returns:
        日志统计信息
    """
    log = logging.getLogger(logger_name)

    return {
        "name": logger_name,
        "level": log.level,
        "handlers_count": len(log.handlers),
        "handlers": [
            {
                "type": type(h).__name__,
                "level": h.level,
                "formatter": type(h.formatter).__name__ if h.formatter else None
            }
            for h in log.handlers
        ]
    }


# 全局日志实例
logger = setup_logger()
