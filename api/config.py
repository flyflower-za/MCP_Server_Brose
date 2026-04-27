"""
配置管理 API
支持动态添加、编辑、启用/禁用服务器
"""
import hmac
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from config import settings, MCP_SERVERS_CONFIG, get_enabled_servers
from utils.auth import verify_basic_auth
from utils.config_manager import get_config_manager


router = APIRouter(prefix="/api/v1/config", tags=["Configuration"])


# 请求模型
class ServerConfigRequest(BaseModel):
    """服务器配置请求"""
    name: str = Field(..., min_length=1, description="服务器名称")
    description: str = Field("", description="服务器描述")
    module: str = Field(..., min_length=1, description="Python 模块路径")
    prefix: str = Field("", description="URL 前缀")
    tags: list = Field(default_factory=list, description="标签列表")
    enabled: bool = Field(True, description="是否启用")


class ServerConfigUpdate(BaseModel):
    """服务器配置更新"""
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    module: Optional[str] = Field(None, min_length=1)
    prefix: Optional[str] = None
    tags: Optional[list] = None
    enabled: Optional[bool] = None


@router.get("/servers")
async def list_all_servers(current_user: str = Depends(verify_basic_auth)):
    """
    获取所有服务器配置(包括已禁用的)

    Returns:
        所有服务器配置
    """
    return {
        "total": len(MCP_SERVERS_CONFIG),
        "servers": {
            server_id: {
                "id": server_id,
                **config,
                "enabled": config.get("enabled", True)
            }
            for server_id, config in MCP_SERVERS_CONFIG.items()
        }
    }


@router.post("/servers")
async def add_server(
    server_id: str,
    config: ServerConfigRequest,
    current_user: str = Depends(verify_basic_auth)
):
    """
    添加新服务器

    Args:
        server_id: 服务器 ID
        config: 服务器配置

    Returns:
        成功消息
    """
    if server_id in MCP_SERVERS_CONFIG:
        raise HTTPException(
            status_code=400,
            detail=f"服务器 {server_id} 已存在"
        )

    # 添加到配置
    MCP_SERVERS_CONFIG[server_id] = {
        "name": config.name,
        "description": config.description,
        "enabled": config.enabled,
        "version": "1.0.0",
        "module": config.module,
        "prefix": config.prefix or f"/{server_id}",
        "tags": config.tags
    }

    # 自动保存到磁盘
    config_manager = get_config_manager()
    config_manager.save_servers(MCP_SERVERS_CONFIG)

    return {
        "success": True,
        "message": f"服务器 {server_id} 已添加并保存",
        "server_id": server_id,
        "config": MCP_SERVERS_CONFIG[server_id]
    }


@router.put("/servers/{server_id}")
async def update_server(
    server_id: str,
    config: ServerConfigUpdate,
    current_user: str = Depends(verify_basic_auth)
):
    """
    更新服务器配置

    Args:
        server_id: 服务器 ID
        config: 更新的配置

    Returns:
        成功消息
    """
    if server_id not in MCP_SERVERS_CONFIG:
        raise HTTPException(
            status_code=404,
            detail=f"服务器 {server_id} 不存在"
        )

    # 更新配置
    current_config = MCP_SERVERS_CONFIG[server_id]
    if config.name is not None:
        current_config["name"] = config.name
    if config.description is not None:
        current_config["description"] = config.description
    if config.module is not None:
        current_config["module"] = config.module
    if config.prefix is not None:
        current_config["prefix"] = config.prefix
    if config.tags is not None:
        current_config["tags"] = config.tags
    if config.enabled is not None:
        current_config["enabled"] = config.enabled

    # 自动保存到磁盘
    config_manager = get_config_manager()
    config_manager.save_servers(MCP_SERVERS_CONFIG)

    return {
        "success": True,
        "message": f"服务器 {server_id} 配置已更新并保存",
        "server_id": server_id,
        "config": current_config
    }


@router.delete("/servers/{server_id}")
async def delete_server(
    server_id: str,
    current_user: str = Depends(verify_basic_auth)
):
    """
    删除服务器配置

    Args:
        server_id: 服务器 ID

    Returns:
        成功消息
    """
    if server_id not in MCP_SERVERS_CONFIG:
        raise HTTPException(
            status_code=404,
            detail=f"服务器 {server_id} 不存在"
        )

    # 保存配置(用于恢复)
    deleted_config = MCP_SERVERS_CONFIG.pop(server_id)

    # 自动保存到磁盘
    config_manager = get_config_manager()
    config_manager.save_servers(MCP_SERVERS_CONFIG)

    return {
        "success": True,
        "message": f"服务器 {server_id} 已删除并保存",
        "server_id": server_id,
        "deleted_config": deleted_config
    }


@router.patch("/servers/{server_id}/toggle")
async def toggle_server(
    server_id: str,
    enabled: bool,
    current_user: str = Depends(verify_basic_auth)
):
    """
    启用/禁用服务器

    Args:
        server_id: 服务器 ID
        enabled: 是否启用

    Returns:
        成功消息
    """
    if server_id not in MCP_SERVERS_CONFIG:
        raise HTTPException(
            status_code=404,
            detail=f"服务器 {server_id} 不存在"
        )

    MCP_SERVERS_CONFIG[server_id]["enabled"] = enabled

    # 自动保存到磁盘
    config_manager = get_config_manager()
    config_manager.save_servers(MCP_SERVERS_CONFIG)

    return {
        "success": True,
        "message": f"服务器 {server_id} 已{'启用' if enabled else '禁用'}并保存",
        "server_id": server_id,
        "enabled": enabled
    }


@router.get("/export")
async def export_config(current_user: str = Depends(verify_basic_auth)):
    """
    导出完整配置

    Returns:
        完整的系统配置
    """
    from config.port_config import get_all_fixed_ports
    from utils.process_manager import get_process_manager
    from utils.config_manager import get_config_manager

    process_manager = get_process_manager()
    config_manager = get_config_manager()

    # 使用配置管理器导出
    return config_manager.export_all()


@router.get("/status")
async def get_config_status(current_user: str = Depends(verify_basic_auth)):
    """
    获取配置存储状态

    Returns:
        配置状态信息
    """
    config_manager = get_config_manager()
    return config_manager.get_status()


@router.post("/save")
async def save_all_configs(current_user: str = Depends(verify_basic_auth)):
    """
    手动保存所有配置到磁盘

    Returns:
        保存结果
    """
    config_manager = get_config_manager()

    # 保存服务器配置
    servers_saved = config_manager.save_servers(MCP_SERVERS_CONFIG)

    # 保存端口配置
    from config.port_config import get_all_fixed_ports
    ports_saved = config_manager.save_ports(get_all_fixed_ports())

    # 保存系统设置
    settings_saved = config_manager.save_settings({
        "auto_restart": settings.PROCESS_AUTO_RESTART,
        "max_restart_count": settings.PROCESS_MAX_RESTART,
        "health_check_interval": settings.PROCESS_HEALTH_CHECK_INTERVAL,
        "log_level": settings.LOG_LEVEL,
        "port_allocation": {
            "base_port": settings.PROCESS_BASE_PORT,
            "max_port": 51250  # 从 PortAllocator 获取
        }
    })

    return {
        "success": all([servers_saved, ports_saved, settings_saved]),
        "message": "配置已保存",
        "servers_saved": servers_saved,
        "ports_saved": ports_saved,
        "settings_saved": settings_saved
    }


@router.post("/import")
async def import_configs(
    overwrite: bool = False,
    current_user: str = Depends(verify_basic_auth)
):
    """
    从磁盘导入配置(重载配置文件)

    Args:
        overwrite: 是否覆盖内存中的配置

    Returns:
        导入结果
    """
    config_manager = get_config_manager()

    # 导入配置
    success = config_manager.import_all(
        config_manager.export_all(),
        overwrite=overwrite
    )

    if success:
        return {
            "success": True,
            "message": "配置导入成功"
        }
    else:
        return {
            "success": False,
            "message": "配置导入失败"
        }
