"""
统一错误处理和异常定义
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class APIError(Exception):
    """API 错误基类"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(APIError):
    """认证错误"""

    def __init__(self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(APIError):
    """授权错误"""

    def __init__(self, message: str = "权限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class NotFoundError(APIError):
    """资源未找到错误"""

    def __init__(self, message: str = "资源未找到", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class ValidationError(APIError):
    """数据验证错误"""

    def __init__(self, message: str = "数据验证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ServiceUnavailableError(APIError):
    """服务不可用错误"""

    def __init__(self, message: str = "服务暂时不可用", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
            details=details
        )


class ProcessStartupError(APIError):
    """进程启动错误"""

    def __init__(self, message: str = "进程启动失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PROCESS_STARTUP_ERROR",
            details=details
        )


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = "ERROR",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    创建标准化的错误响应

    Args:
        status_code: HTTP 状态码
        message: 错误消息
        error_code: 错误代码
        details: 额外详情

    Returns:
        JSONResponse: 标准化的错误响应
    """
    error_content = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        }
    }

    return JSONResponse(status_code=status_code, content=error_content)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """处理自定义 API 错误"""
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理 FastAPI HTTPException"""
    # 将 HTTPException 转换为标准错误格式
    error_code_map = {
        401: "AUTHENTICATION_ERROR",
        403: "AUTHORIZATION_ERROR",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }

    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")

    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        error_code=error_code
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获的异常"""
    import logging
    import traceback

    # 记录完整的异常堆栈
    logging.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="服务器内部错误",
        error_code="INTERNAL_ERROR",
        details={"type": type(exc).__name__}
    )


def setup_error_handlers(app):
    """
    为 FastAPI 应用设置错误处理器

    Args:
        app: FastAPI 应用实例
    """
    from fastapi.exceptions import RequestValidationError

    # 自定义 API 错误
    app.add_exception_handler(APIError, api_error_handler)

    # FastAPI HTTPException
    app.add_exception_handler(HTTPException, http_exception_handler)

    # 请求验证错误
    app.add_exception_handler(RequestValidationError, lambda request, exc: create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        message="请求参数验证失败",
        error_code="VALIDATION_ERROR",
        details={"errors": exc.errors()}
    ))

    # 通用异常处理器
    app.add_exception_handler(Exception, general_exception_handler)
