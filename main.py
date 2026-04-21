#!/usr/bin/env python3
"""
MCP服务器管理系统 - 主入口（进程隔离架构）
"""
from typing import Dict

import secrets
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from config import settings, get_enabled_servers
from config.port_config import get_fixed_port, set_fixed_port, remove_fixed_port, get_all_fixed_ports
from utils.logger import logger
from utils.process_manager import get_process_manager
from middleware.proxy_middleware import ProxyMiddleware


# 创建FastAPI应用（API网关）
app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 添加请求转发中间件（不传递参数）
app.add_middleware(ProxyMiddleware)

# 获取进程管理器
process_manager = get_process_manager()


# 安全认证
security = HTTPBasic()

def verify_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """基础身份验证"""
    correct_username = secrets.compare_digest(credentials.username, settings.DASHBOARD_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.DASHBOARD_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# API模型
class ServerActionResponse(BaseModel):
    """服务器操作响应"""
    success: bool
    message: str
    server_id: str
    status: dict


# 启动所有服务器
def start_all_servers():
    """启动所有已启用的MCP服务器"""
    enabled_servers = get_enabled_servers()
    logger.info(f"开始启动MCP服务器，共 {len(enabled_servers)} 个已启用")

    started_count = 0
    failed_servers = []

    for server_id, server_config in enabled_servers.items():
        if process_manager.start_server(server_id, server_config):
            started_count += 1
        else:
            failed_servers.append(server_id)

    logger.info(f"MCP服务器启动完成: {started_count}/{len(enabled_servers)} 成功")

    if failed_servers:
        logger.warning(f"启动失败的服务器: {', '.join(failed_servers)}")

    return started_count, failed_servers


# Dashboard 控制台
@app.get("/dashboard", dependencies=[Depends(verify_auth)])
async def dashboard():
    """管理控制台可视化界面"""
    from pathlib import Path
    dashboard_path = Path(__file__).parent / "dashboard" / "index.html"
    if not dashboard_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard UI not found")
    return FileResponse(str(dashboard_path))


# 根路径
@app.get("/")
async def root():
    """根路径 - 重定向到管理控制台"""
    return RedirectResponse(url="/dashboard")


# 健康检查
@app.get("/health")
async def health_check():
    """系统健康检查"""
    all_statuses = process_manager.get_all_statuses()

    running_count = sum(1 for s in all_statuses.values() if s.get("status") == "running")

    return {
        "status": "healthy",
        "architecture": "process_isolation",
        "loaded_servers": len(process_manager.processes),
        "running_servers": running_count,
        "servers": list(process_manager.processes.keys())
    }


# 服务器列表
@app.get("/api/v1/servers", dependencies=[Depends(verify_auth)])
async def list_servers():
    """列出所有MCP服务器"""
    enabled_servers = get_enabled_servers()
    all_statuses = process_manager.get_all_statuses()

    servers_list = []
    for server_id, config in enabled_servers.items():
        server_info = {
            "id": server_id,
            **config,
            "runtime_status": all_statuses.get(server_id, {"status": "not_initialized"})
        }
        servers_list.append(server_info)

    return {
        "total": len(servers_list),
        "servers": servers_list
    }


# 获取单个服务器状态
@app.get("/api/v1/servers/{server_id}/status", dependencies=[Depends(verify_auth)])
async def get_server_status(server_id: str):
    """获取单个服务器的详细状态"""
    enabled_servers = get_enabled_servers()

    if server_id not in enabled_servers:
        raise HTTPException(status_code=404, detail=f"服务器 {server_id} 不存在")

    status = process_manager.get_server_status(server_id)
    return status


# 启动单个服务器
@app.post("/api/v1/servers/{server_id}/start", response_model=ServerActionResponse, dependencies=[Depends(verify_auth)])
async def start_server(server_id: str):
    """启动单个服务器"""
    enabled_servers = get_enabled_servers()

    if server_id not in enabled_servers:
        raise HTTPException(status_code=404, detail=f"服务器 {server_id} 不存在")

    config = enabled_servers[server_id]
    success = process_manager.start_server(server_id, config)

    return ServerActionResponse(
        success=success,
        message="服务器启动成功" if success else "服务器启动失败",
        server_id=server_id,
        status=process_manager.get_server_status(server_id)
    )


# 停止单个服务器
@app.post("/api/v1/servers/{server_id}/stop", response_model=ServerActionResponse, dependencies=[Depends(verify_auth)])
async def stop_server(server_id: str):
    """停止单个服务器"""
    enabled_servers = get_enabled_servers()

    if server_id not in enabled_servers:
        raise HTTPException(status_code=404, detail=f"服务器 {server_id} 不存在")

    success = process_manager.stop_server(server_id)

    return ServerActionResponse(
        success=success,
        message="服务器停止成功" if success else "服务器停止失败",
        server_id=server_id,
        status=process_manager.get_server_status(server_id)
    )


# 重启单个服务器
@app.post("/api/v1/servers/{server_id}/restart", response_model=ServerActionResponse, dependencies=[Depends(verify_auth)])
async def restart_server(server_id: str):
    """重启单个服务器"""
    enabled_servers = get_enabled_servers()

    if server_id not in enabled_servers:
        raise HTTPException(status_code=404, detail=f"服务器 {server_id} 不存在")

    config = enabled_servers[server_id]
    success = process_manager.restart_server(server_id, config)

    return ServerActionResponse(
        success=success,
        message="服务器重启成功" if success else "服务器重启失败",
        server_id=server_id,
        status=process_manager.get_server_status(server_id)
    )


# 获取所有服务器状态（无需认证，方便监控）
@app.get("/api/v1/servers/statuses")
async def get_all_server_statuses():
    """获取所有服务器的状态"""
    return process_manager.get_all_statuses()


# 启动所有服务器
@app.post("/api/v1/servers/start-all", dependencies=[Depends(verify_auth)])
async def start_all_servers_endpoint():
    """启动所有服务器"""
    started_count, failed_servers = start_all_servers()

    return {
        "success": True,
        "started_count": started_count,
        "failed_servers": failed_servers,
        "message": f"已启动 {started_count} 个服务器"
    }


# 停止所有服务器
@app.post("/api/v1/servers/stop-all", dependencies=[Depends(verify_auth)])
async def stop_all_servers():
    """停止所有服务器"""
    stopped_count = 0
    failed_servers = []

    for server_id in list(process_manager.processes.keys()):
        if process_manager.stop_server(server_id):
            stopped_count += 1
        else:
            failed_servers.append(server_id)

    return {
        "success": True,
        "stopped_count": stopped_count,
        "failed_servers": failed_servers,
        "message": f"已停止 {stopped_count} 个服务器"
    }



# ─────────────────────────────────────────────
# 固定端口配置 API
# ─────────────────────────────────────────────

class PortConfigRequest(BaseModel):
    """固定端口配置请求"""
    port: int


@app.get("/api/v1/servers/port-configs", dependencies=[Depends(verify_auth)])
async def get_all_port_configs():
    """获取全部服务器的固定端口配置"""
    enabled = get_enabled_servers()
    fixed = get_all_fixed_ports()
    result = {}
    for server_id in enabled:
        result[server_id] = {
            "server_id": server_id,
            "fixed_port": fixed.get(server_id),
            "mode": "fixed" if server_id in fixed else "dynamic",
        }
    return result


@app.get("/api/v1/servers/{server_id}/port-config", dependencies=[Depends(verify_auth)])
async def get_port_config(server_id: str):
    """获取单个服务器的固定端口配置"""
    enabled = get_enabled_servers()
    if server_id not in enabled:
        raise HTTPException(status_code=404, detail=f"服务器 {server_id} 不存在")
    fixed_port = get_fixed_port(server_id)
    return {
        "server_id": server_id,
        "fixed_port": fixed_port,
        "mode": "fixed" if fixed_port else "dynamic",
    }


@app.put("/api/v1/servers/{server_id}/port-config", dependencies=[Depends(verify_auth)])
async def set_port_config(server_id: str, body: PortConfigRequest):
    """设置服务器固定端口（立即持久化，下次启动生效）"""
    enabled = get_enabled_servers()
    if server_id not in enabled:
        raise HTTPException(status_code=404, detail=f"服务器 {server_id} 不存在")
    try:
        set_fixed_port(server_id, body.port)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    logger.info(f"🔧 服务器 {server_id} 固定端口已设置为 {body.port}")
    return {
        "success": True,
        "server_id": server_id,
        "fixed_port": body.port,
        "message": f"固定端口已保存，重启后生效",
    }


@app.delete("/api/v1/servers/{server_id}/port-config", dependencies=[Depends(verify_auth)])
async def delete_port_config(server_id: str):
    """删除服务器固定端口配置（恢复动态分配）"""
    enabled = get_enabled_servers()
    if server_id not in enabled:
        raise HTTPException(status_code=404, detail=f"服务器 {server_id} 不存在")
    existed = remove_fixed_port(server_id)
    logger.info(f"🔧 服务器 {server_id} 固定端口已移除，将使用动态端口分配")
    return {
        "success": True,
        "server_id": server_id,
        "existed": existed,
        "mode": "dynamic",
        "message": "固定端口已移除，下次启动将动态分配",
    }


def main():
    """启动服务器"""
    logger.info("=" * 60)
    logger.info(f"启动 {settings.TITLE} v{settings.VERSION}")
    logger.info("架构: 进程隔离模式")
    logger.info("=" * 60)

    # 启动所有MCP服务器进程
    logger.info("正在启动所有MCP服务器进程...")
    start_all_servers()

    logger.info(f"API网关将在 {settings.HOST}:{settings.PORT} 启动")
    logger.info(f"API文档: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🌟 Dashboard 控制台: http://{settings.HOST}:{settings.PORT}/dashboard")
    logger.info("")
    logger.info("服务器管理API:")
    logger.info(f"  - GET  /api/v1/servers/statuses     # 查看所有服务器状态")
    logger.info(f"  - POST /api/v1/servers/{{id}}/restart # 重启单个服务器")
    logger.info(f"  - POST /api/v1/servers/{{id}}/stop    # 停止单个服务器")
    logger.info(f"  - POST /api/v1/servers/{{id}}/start   # 启动单个服务器")
    logger.info("")

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()