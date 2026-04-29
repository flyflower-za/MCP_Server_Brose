"""
认证中间件 - 保护敏感端点
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED
import hmac
from typing import Optional

from config import settings
from utils.logger import logger
from utils.security import token_manager


class AuthMiddleware(BaseHTTPMiddleware):
    """
    认证中间件 - 当认证启用时保护敏感端点
    """

    # 不需要认证的路径
    PUBLIC_PATHS = {
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/favicon.ico",
        "/static",
        "/dashboard",  # 允许访问Dashboard HTML，登录由前端控制
    }

    # 需要认证的路径前缀
    PROTECTED_PREFIXES = {
        # "/dashboard",  # 移除：Dashboard HTML可以访问，API由前端控制
        "/api/v1/servers",
        "/api/v1/system",
        "/api/v1/config",
        "/api/v1/tasks",
        "/api/v1/proxy",
    }

    async def dispatch(self, request: Request, call_next):
        """处理请求，进行认证检查"""

        path = request.url.path

        # 如果认证被禁用，直接放行
        if not settings.DASHBOARD_AUTH_ENABLED:
            logger.debug(f"认证已禁用，放行请求: {path}")
            return await call_next(request)

        # 检查是否是公开路径
        if self._is_public_path(path):
            logger.debug(f"公开路径，放行请求: {path}")
            return await call_next(request)

        # 检查是否是受保护路径
        if self._is_protected_path(path):
            logger.info(f"🔒 受保护路径需要认证: {path}")

            # 验证认证
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                logger.warning(f"❌ 缺少认证头: {path}")
                return self._auth_required_response()

            # 支持两种认证方式：
            # 1. Bearer Token (JWT，会过期)
            # 2. ApiKey (永久有效，用于插件集成)

            logger.info(f"🔍 认证检查: {path}, Auth Header: {auth_header[:20]}...")

            if auth_header.startswith("Bearer "):
                # JWT Token 认证
                token = auth_header[7:]  # 移除 "Bearer " 前缀

                # 验证 token
                payload = token_manager.verify_token(token)
                if payload is not None:
                    request.state.user = payload
                    logger.debug(f"✅ JWT Token验证成功: {path}")
                    return await call_next(request)  # ← 添加这行！
                else:
                    logger.warning(f"❌ JWT Token验证失败: {path}")
                    return self._auth_required_response()

            elif auth_header.startswith("ApiKey "):
                # API Key 认证（永久有效，用于插件集成）
                api_key = auth_header[7:]  # 移除 "ApiKey " 前缀（7个字符）

                # 验证 API Key
                if self._validate_api_key(api_key):
                    request.state.user = {"username": "api_user", "type": "api_key"}
                    logger.debug(f"✅ API Key验证成功: {path}")
                    return await call_next(request)  # ← 添加这行！
                else:
                    logger.warning(f"❌ API Key验证失败: {path}")
                    return self._auth_required_response()

            else:
                logger.warning(f"❌ 无效的认证类型: {path}")
                return self._auth_required_response()

        # 放行请求
        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """检查是否是公开路径"""
        # 精确匹配公开路径
        if path in self.PUBLIC_PATHS:
            return True

        # 前缀匹配公开路径
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True

        return False

    def _is_protected_path(self, path: str) -> bool:
        """检查是否是受保护路径"""
        for prefix in self.PROTECTED_PREFIXES:
            if path.startswith(prefix):
                return True
        return False

    def _validate_api_key(self, api_key: str) -> bool:
        """
        验证API Key（永久有效，用于插件集成）

        Args:
            api_key: API Key字符串

        Returns:
            是否有效
        """
        # 从环境变量获取配置的API Key
        configured_key = getattr(settings, 'API_KEY', None)

        # 调试日志
        logger.info(f"API Key验证请求: received={api_key[:10]}... configured={configured_key[:10]}...")

        if not configured_key or configured_key == "your-permanent-api-key-change-this":
            logger.warning("API_KEY未配置或使用默认值，API Key认证失败")
            return False

        # 使用恒定时间比较，防止时序攻击
        import hmac
        result = hmac.compare_digest(api_key, configured_key)
        logger.info(f"API Key验证结果: {result}")
        return result

    def _auth_required_response(self):
        """返回认证失败响应"""
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Authentication required",
                "message": "请先登录访问此资源",
                "auth_enabled": True
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


class OptionalAuthMiddleware(BaseHTTPMiddleware):
    """
    可选认证中间件 - 允许匿名访问，但支持认证用户
    """

    async def dispatch(self, request: Request, call_next):
        """处理请求，可选认证"""

        # 如果认证被禁用，直接放行
        if not settings.DASHBOARD_AUTH_ENABLED:
            return await call_next(request)

        # 尝试验证认证
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            payload = token_manager.verify_token(token)
            if payload:
                # Token 有效，将用户信息添加到请求状态
                request.state.user = payload

        # 放行请求（无论是否认证）
        return await call_next(request)
