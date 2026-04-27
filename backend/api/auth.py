"""
认证 API 路由 - 用户注册、登录、登出
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import re

from core import get_db
from core.auth import (
    get_password_hash, verify_password, create_access_token, decode_access_token
)
from models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，未登录返回 None）"""
    if not token:
        return None
    
    payload = decode_access_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


def require_auth(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """要求用户已登录"""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="未登录或登录已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def validate_username(username: str) -> bool:
    """验证用户名格式：字母、数字、下划线，3-20字符"""
    if not username or len(username) < 3 or len(username) > 20:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))


def validate_password(password: str) -> tuple[bool, str]:
    """验证密码强度，返回 (是否有效, 错误信息)"""
    if not password:
        return False, "密码不能为空"
    if len(password) < 6:
        return False, "密码至少需要6个字符"
    return True, ""


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 验证用户名
    if not validate_username(data.username):
        raise HTTPException(
            status_code=400,
            detail="用户名格式错误：需3-20个字符，只能包含字母、数字和下划线"
        )
    
    # 验证密码
    valid, msg = validate_password(data.password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user = User(
        username=data.username,
        email=data.email,
        name=data.name or data.username,
        password_hash=get_password_hash(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 生成 token
    token = create_access_token(user.id, user.username)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            name=user.name
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == data.username).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not verify_password(data.password, user.password_hash or ""):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 生成 token
    token = create_access_token(user.id, user.username)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            name=user.name
        )
    )


@router.post("/login/form", response_model=TokenResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 表单登录（用于兼容）"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not verify_password(form_data.password, user.password_hash or ""):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = create_access_token(user.id, user.username)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            name=user.name
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_auth)):
    """获取当前用户信息"""
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        name=user.name
    )


@router.post("/logout")
async def logout(user: User = Depends(require_auth)):
    """登出（前端删除 token 即可）"""
    return {"message": "已成功登出"}
