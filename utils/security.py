"""
认证和安全工具
支持密码哈希、JWT Token 生成和验证
"""
import os
import hashlib
import hmac
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


class PasswordManager:
    """密码管理器 - 支持密码哈希和验证"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希（使用 HMAC-SHA256）

        Args:
            password: 明文密码

        Returns:
            哈希后的密码（十六进制字符串）
        """
        # 使用 HMAC-SHA256 替代 bcrypt（无需额外依赖）
        salt = os.urandom(32).hex()
        password_hash = hmac.new(
            salt.encode(),
            password.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{salt}:{password_hash}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        验证密码是否匹配

        Args:
            password: 明文密码
            password_hash: 哈希后的密码

        Returns:
            是否匹配
        """
        try:
            salt, hash_value = password_hash.split(':')
            computed_hash = hmac.new(
                salt.encode(),
                password.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(computed_hash, hash_value)
        except (ValueError, AttributeError):
            return False


class TokenManager:
    """JWT Token 管理器"""

    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化 Token 管理器

        Args:
            secret_key: JWT 密钥（从环境变量读取或自动生成）
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            # 如果没有设置密钥，使用环境变量生成一个
            self.secret_key = os.getenv("MCP_HOST", "default-secret-key")
            print("⚠️  警告: 使用默认 JWT 密钥，生产环境请设置 JWT_SECRET_KEY 环境变量")

        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 小时

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        创建访问 Token

        Args:
            data: 要编码到 Token 中的数据

        Returns:
            JWT Token 字符串
        """
        to_encode = data.copy()

        # 设置过期时间
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})

        # 生成 Token
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证 Token 并返回解码后的数据

        Args:
            token: JWT Token 字符串

        Returns:
            解码后的数据，验证失败返回 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None


class SecurityConfig:
    """安全配置"""

    # 密码策略
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = False
    REQUIRE_LOWERCASE = False
    REQUIRE_DIGIT = False
    REQUIRE_SPECIAL = False

    # Token 策略
    TOKEN_EXPIRE_HOURS = 24

    # 速率限制
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100  # 每小时请求数
    RATE_LIMIT_WINDOW = 3600  # 时间窗口（秒）

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        验证密码强度

        Args:
            password: 密码字符串

        Returns:
            是否符合要求
        """
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            return False

        # 可选：添加更多密码规则
        # if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        #     return False
        # if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        #     return False
        # if SecurityConfig.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        #     return False

        return True


# 全局实例
password_manager = PasswordManager()
token_manager = TokenManager()
