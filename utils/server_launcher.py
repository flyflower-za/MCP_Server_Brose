#!/usr/bin/env python3
"""
服务器进程启动器
用于启动独立的MCP服务器进程
"""
import argparse
import sys
import importlib
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from config import settings
from utils.logger import logger


class ServerAuthMiddleware(BaseHTTPMiddleware):
    """
    MCP服务器认证中间件
    验证API Key或JWT Token
    """

    async def dispatch(self, request: Request, call_next):
        """处理请求，进行认证检查"""

        # 如果认证被禁用，直接放行
        if not settings.DASHBOARD_AUTH_ENABLED:
            return await call_next(request)

        # 健康检查端点不需要认证
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # 验证认证
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required", "message": "请提供API Key或Token"},
            )

        # 支持两种认证方式
        if auth_header.startswith("Bearer "):
            # JWT Token 认证
            from utils.security import token_manager
            token = auth_header[7:]
            payload = token_manager.verify_token(token)
            if payload is not None:
                return await call_next(request)
            else:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        elif auth_header.startswith("ApiKey "):
            # API Key 认证
            import hmac
            api_key = auth_header[7:]
            configured_key = settings.API_KEY

            if not configured_key or configured_key == "your-permanent-api-key-change-this":
                return JSONResponse(status_code=401, content={"detail": "API Key not configured"})

            if hmac.compare_digest(api_key, configured_key):
                return await call_next(request)
            else:
                return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

        return JSONResponse(status_code=401, content={"detail": "Unsupported authentication type"})


def create_server_app(module_path: str, server_id: str) -> FastAPI:
    """
    创建单个服务器的FastAPI应用

    Args:
        module_path: 服务器模块路径
        server_id: 服务器ID

    Returns:
        FastAPI应用实例
    """
    # 创建FastAPI应用
    app = FastAPI(
        title=f"{server_id} Server",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # 添加认证中间件
    if settings.DASHBOARD_AUTH_ENABLED:
        app.add_middleware(ServerAuthMiddleware)

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    try:
        # 动态导入服务器模块
        module = importlib.import_module(module_path)

        # 获取路由器
        router = getattr(module, 'router', None)
        info_func = getattr(module, 'get_info', None)

        if router:
            # 直接注册路由器（不加前缀，因为每个进程只有一个服务器）
            app.include_router(router)
            logger.info(f"✅ 成功加载服务器模块: {module_path}")

            # 添加服务器信息端点
            @app.get("/")
            async def server_info():
                """服务器信息"""
                info = info_func() if info_func else {}
                return {
                    "server_id": server_id,
                    "module": module_path,
                    **info
                }

            # 添加健康检查端点
            @app.get("/health")
            async def health():
                """健康检查"""
                return {"status": "healthy", "server_id": server_id}

        else:
            logger.error(f"模块 {module_path} 中没有找到router")
            sys.exit(1)

    except ImportError as e:
        logger.error(f"无法导入模块 {module_path}: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"加载服务器模块失败: {str(e)}")
        sys.exit(1)

    return app


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="MCP服务器进程启动器")
    parser.add_argument("--server-id", required=True, help="服务器ID")
    parser.add_argument("--module", required=True, help="服务器模块路径")
    parser.add_argument("--port", type=int, required=True, help="监听端口")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址（默认0.0.0.0允许外部访问）")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info(f"启动MCP服务器进程: {args.server_id}")
    logger.info("=" * 60)
    logger.info(f"模块: {args.module}")
    logger.info(f"地址: {args.host}:{args.port}")
    logger.info("")

    # 创建服务器应用
    app = create_server_app(args.module, args.server_id)

    # 启动服务器
    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info(f"服务器 {args.server_id} 被用户中断")
    except Exception as e:
        logger.error(f"服务器 {args.server_id} 运行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()