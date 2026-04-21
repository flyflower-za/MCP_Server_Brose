"""
系统监控和管理 API
"""
import os
import psutil
from typing import Dict, Any
from fastapi import APIRouter

from config import settings
from utils.port_allocator import get_port_allocator
from utils.process_manager import get_process_manager


router = APIRouter(prefix="/api/v1/system", tags=["System"])


@router.get("/resources")
async def get_system_resources() -> Dict[str, Any]:
    """
    获取系统资源使用情况

    Returns:
        系统资源信息（CPU、内存、端口池等）
    """
    process = psutil.Process()

    # CPU 使用率
    try:
        cpu_percent = process.cpu_percent(interval=0.1)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        cpu_percent = 0.0

    # 内存使用
    try:
        mem_info = process.memory_info()
        memory_mb = mem_info.rss / 1024 / 1024  # 转换为 MB
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        memory_mb = 0.0

    # 端口池状态
    port_allocator = get_port_allocator()
    allocated_ports = port_allocator.get_allocated_ports()
    port_pool_status = {
        "base_port": port_allocator.base_port,
        "max_port": port_allocator.max_port,
        "current_port": port_allocator.current_port,
        "allocated_count": len(allocated_ports),
        "allocated_ports": list(allocated_ports),
        "total_ports": port_allocator.max_port - port_allocator.base_port + 1,
        "available_ports": port_allocator.max_port - port_allocator.base_port + 1 - len(allocated_ports)
    }

    # 进程管理器状态
    process_manager = get_process_manager()
    process_status = {
        "total_processes": len(process_manager.processes),
        "running_processes": sum(
            1 for s in process_manager.get_all_statuses().values()
            if s.get("status") == "running"
        ),
        "max_restart": process_manager.max_restart
    }

    return {
        "hub": {
            "cpu_percent": round(cpu_percent, 2),
            "memory_mb": round(memory_mb, 2),
            "pid": os.getpid(),
        },
        "port_pool": port_pool_status,
        "processes": process_status,
    }


@router.get("/info")
async def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息

    Returns:
        系统信息（版本、配置等）
    """
    return {
        "system": settings.TITLE,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "api_prefix": settings.API_PREFIX,
        "architecture": "process_isolation",
        "debug": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "log_level": settings.LOG_LEVEL,
    }


@router.get("/export")
async def export_config() -> Dict[str, Any]:
    """
    导出系统配置

    Returns:
        完整的系统配置（用于备份或迁移）
    """
    from config import MCP_SERVERS_CONFIG, get_enabled_servers
    from config.port_config import get_all_fixed_ports

    process_manager = get_process_manager()
    port_allocator = get_port_allocator()

    return {
        "version": "1.0.0",
        "exported_at": psutil.boot_time().isoformat(),
        "settings": {
            "host": settings.HOST,
            "port": settings.PORT,
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
        },
        "servers": MCP_SERVERS_CONFIG,
        "enabled_servers": list(get_enabled_servers().keys()),
        "fixed_ports": get_all_fixed_ports(),
        "current_status": {
            "running_servers": list(process_manager.processes.keys()),
            "allocated_ports": list(port_allocator.get_allocated_ports()),
        }
    }
