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
    获取所有服务器配置（包括已禁用的）

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

    return {
        "success": True,
        "message": f"服务器 {server_id} 已添加",
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

    return {
        "success": True,
        "message": f"服务器 {server_id} 配置已更新",
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

    # 保存配置（用于恢复）
    deleted_config = MCP_SERVERS_CONFIG.pop(server_id)

    return {
        "success": True,
        "message": f"服务器 {server_id} 已删除",
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

    return {
        "success": True,
        "message": f"服务器 {server_id} 已{'启用' if enabled else '禁用'}",
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

    process_manager = get_process_manager()

    return {
        "version": "1.0.0",
        "mcp_servers": MCP_SERVERS_CONFIG,
        "enabled_servers": list(get_enabled_servers().keys()),
        "fixed_ports": get_all_fixed_ports(),
        "running_servers": list(process_manager.processes.keys())
    }
