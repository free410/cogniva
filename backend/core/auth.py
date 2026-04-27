"""
认证工具模块 - JWT Token 管理
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
import hashlib
import secrets
from jose import JWTError, jwt
from core.config import settings

# JWT 配置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def get_password_hash(password: str) -> str:
    """哈希密码 - 使用 SHA256 + salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode())
    return f"{salt}${hash_obj.hexdigest()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    if not hashed_password or '$' not in hashed_password:
        return False
    try:
        salt, stored_hash = hashed_password.split('$', 1)
        hash_obj = hashlib.sha256((salt + plain_password).encode())
        return hash_obj.hexdigest() == stored_hash
    except (ValueError, AttributeError):
        return False


def create_access_token(user_id: uuid.UUID, username: str) -> str:
    """创建访问令牌"""
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "username": username,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.APP_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, settings.APP_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[uuid.UUID]:
    """从 token 中获取用户 ID"""
    payload = decode_access_token(token)
    if payload:
        try:
            return uuid.UUID(payload.get("sub"))
        except (ValueError, TypeError):
            return None
    return None
