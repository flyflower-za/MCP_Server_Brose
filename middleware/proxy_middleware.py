"""
请求转发中间件
将API网关的请求转发到对应的服务器进程
"""
import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from utils.logger import logger
from utils.process_manager import get_process_manager


class ProxyMiddleware(BaseHTTPMiddleware):
    """请求转发中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.process_manager = get_process_manager()
        # 从配置读取超时时间
        from config.settings import settings
        timeout = settings.REQUEST_TIMEOUT
        self.client = httpx.AsyncClient(timeout=timeout)

    async def dispatch(self, request: Request, call_next):
        """
        处理请求转发

        Args:
            request: 传入请求
            call_next: 下一个中间件/处理器

        Returns:
            响应
        """
        logger.info(f"📨 代理收到请求: {request.url.path} ({request.method})")

        # 跳过管理端点和系统端点
        if await self._should_skip(request):
            logger.info(f"⏭️  跳过转发: {request.url.path}")
            return await call_next(request)

        # 解析请求路径，确定目标服务器
        server_id = await self._parse_server_id(request)

        if server_id is None:
            # 无法解析服务器ID，返回404
            return JSONResponse(
                status_code=404,
                content={"error": "未找到对应的服务器", "path": request.url.path}
            )

        # 获取服务器状态
        server_status = self.process_manager.get_server_status(server_id)

        if server_status["status"] != "running":
            # 服务器未运行
            return JSONResponse(
                status_code=503,
                content={
                    "error": f"服务器 {server_id} 未运行",
                    "status": server_status["status"]
                }
            )

        # 移除前缀并构建目标URL
        from config.settings import MCP_SERVERS_CONFIG
        server_config = MCP_SERVERS_CONFIG.get(server_id, {})
        prefix = server_config.get("prefix", "")

        # 移除路径前缀
        path = request.url.path
        if path.startswith(prefix):
            path = path[len(prefix):]

        target_url = f"http://127.0.0.1:{server_status['port']}{path}"
        logger.info(f"🔄 转发请求到: {target_url}")

        try:
            # 转发请求
            response = await self._forward_request(request, target_url)
            return response

        except Exception as e:
            logger.error(f"转发请求失败: {str(e)}")
            return JSONResponse(
                status_code=502,
                content={"error": "请求转发失败", "message": str(e)}
            )

    async def _should_skip(self, request: Request) -> bool:
        """
        判断是否跳过转发

        Args:
            request: 传入请求

        Returns:
            是否跳过
        """
        path = request.url.path

        # 精确匹配的路径
        exact_matches = ["/", "/health"]
        if path in exact_matches:
            return True

        # 前缀匹配的路径（需要确保不会误匹配其他路径）
        skip_prefixes = [
            "/docs",          # API 文档
            "/redoc",         # ReDoc 文档
            "/openapi.json",  # OpenAPI schema
            "/api/v1/servers",# 管理端点
            "/api/v1/auth",   # 认证端点
            "/api/v1/config", # 配置管理端点
            "/api/v1/system", # 系统监控端点
            "/static",        # 静态文件
            "/dashboard",     # Dashboard
        ]

        # 检查路径是否匹配
        for prefix in skip_prefixes:
            if path.startswith(prefix):
                return True

        return False

    async def _parse_server_id(self, request: Request) -> str:
        """
        从请求路径解析服务器ID

        Args:
            request: 传入请求

        Returns:
            服务器ID，如果无法解析则返回None
        """
        # 路径格式: /pdf/extract -> pdf_extractor
        # 从配置中找到对应的前缀
        from config.settings import MCP_SERVERS_CONFIG

        path_parts = request.url.path.strip("/").split("/")

        if not path_parts:
            return None

        # 获取路径的第一部分作为前缀
        prefix = f"/{path_parts[0]}"
        logger.info(f"🔍 解析路径: {request.url.path} -> 前缀: {prefix}")

        # 查找对应的服务器
        for server_id, config in MCP_SERVERS_CONFIG.items():
            if config.get("prefix") == prefix:
                logger.info(f"✅ 找到服务器: {server_id}")
                return server_id

        logger.warning(f"❌ 未找到对应的服务器 (前缀: {prefix})")
        return None

    async def _forward_request(self, request: Request, target_url: str) -> Response:
        """
        转发HTTP请求

        Args:
            request: 原始请求
            target_url: 目标URL

        Returns:
            转发的响应
        """
        # 准备请求体
        body = await request.body()

        # 构建请求头
        headers = dict(request.headers)
        headers.pop("host", None)  # 移除host头

        try:
            # 发送请求
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )

            # 返回响应
            return JSONResponse(
                status_code=response.status_code,
                content=response.json(),
                headers=dict(response.headers)
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP请求失败: {str(e)}")
            raise