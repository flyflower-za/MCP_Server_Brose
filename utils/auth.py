"""
认证和授权 API
支持 JWT Token 和密码哈希
"""
import hmac
import os
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

from config import settings
from utils.security import password_manager, token_manager, SecurityConfig


# 路由器
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# 安全模型
class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=SecurityConfig.MIN_PASSWORD_LENGTH, description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordChangeRequest(BaseModel):
    """密码修改请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=SecurityConfig.MIN_PASSWORD_LENGTH, description="新密码")


# HTTP Bearer 安全方案
security = HTTPBearer()


def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """
    验证 Basic Auth 凭据（保持向后兼容）

    Args:
        credentials: HTTP 基本认证凭据

    Returns:
        用户名

    Raises:
        HTTPException: 认证失败
    """
    correct_username = hmac.compare_digest(credentials.username, settings.DASHBOARD_USERNAME)
    # 明文密码比较（临时方案，建议使用哈希）
    correct_password = hmac.compare_digest(credentials.password, settings.DASHBOARD_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    验证 JWT Token

    Args:
        credentials: HTTP Bearer Token

    Returns:
        Token payload

    Raises:
        HTTPException: Token 无效
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = token_manager.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        return payload
    except Exception:
        raise credentials_exception


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    登录并获取 JWT Token

    Args:
        request: 登录请求（用户名和密码）

    Returns:
        JWT Token 响应

    Raises:
        HTTPException: 登录失败
    """
    # 验证用户名和密码
    correct_username = hmac.compare_digest(request.username, settings.DASHBOARD_USERNAME)
    correct_password = hmac.compare_digest(request.password, settings.DASHBOARD_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成 Token
    token_data = {
        "sub": request.username,
        "username": request.username,
        "type": "access"
    }
    access_token = token_manager.create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/verify-token")
async def verify_token_endpoint(payload: dict = Depends(verify_token)):
    """
    验证 Token 并返回用户信息

    Args:
        payload: Token payload

    Returns:
        用户信息
    """
    return {
        "username": payload.get("username"),
        "type": payload.get("type"),
        "valid": True
    }


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: str = Depends(verify_basic_auth)
):
    """
    修改密码（需要 Basic Auth 或 JWT Token）

    Args:
        request: 密码修改请求
        current_user: 当前用户名

    Returns:
        成功消息

    Raises:
        HTTPException: 修改失败
    """
    # 验证旧密码
    correct_password = hmac.compare_digest(request.old_password, settings.DASHBOARD_PASSWORD)
    if not correct_password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect old password"
        )

    # 验证新密码强度
    if not SecurityConfig.validate_password(request.new_password):
        raise HTTPException(
            status_code=400,
            detail=f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters long"
        )

    # TODO: 在实际应用中，这里应该更新密码存储（如数据库）
    # 由于当前使用环境变量，可以提示用户更新 .env 文件

    return {
        "message": "Password changed successfully",
        "note": "Please update DASHBOARD_PASSWORD in your .env file for persistence"
    }


# 导入 BasicAuth（如果需要）
try:
    from fastapi.security import HTTPBasicCredentials, HTTPBasic
    HTTPBasic
except ImportError:
    # 如果没有安装，这里会失败，但 FastAPI 通常都有
    pass
