from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from core.database import SessionLocal
from core import get_db
from core.config import settings
from models import User
from api.auth import require_auth
import httpx
import asyncio

router = APIRouter(prefix="/api/settings", tags=["settings"])


class LLMProviderConfig(BaseModel):
    provider: str
    model: Optional[str] = None
    api_url: Optional[str] = None


class SettingsUpdate(BaseModel):
    default_provider: Optional[str] = None
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None
    dashscope_key: Optional[str] = None


class ProviderStatus(BaseModel):
    name: str
    display_name: str
    available: bool
    models: List[str]
    error: Optional[str] = None


class DatabaseStatus(BaseModel):
    connected: bool
    host: str
    database: str
    vector_dimension: int
    status: str


@router.get("/", response_model=Dict[str, Any])
async def get_settings(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """获取当前配置：用户设置优先，缺省回落到环境变量"""
    saved = user.settings if isinstance(user.settings, dict) else {}
    return {
        "default_provider": saved.get("default_provider") or getattr(settings, 'DEFAULT_PROVIDER', 'deepseek'),
        "ollama_url": saved.get("ollama_url") or settings.OLLAMA_BASE_URL,
        "ollama_model": saved.get("ollama_model") or settings.OLLAMA_MODEL,
        "openai_key": "***" if settings.OPENAI_API_KEY else "",
        "anthropic_key": "***" if settings.ANTHROPIC_API_KEY else "",
        "dashscope_key": "***" if settings.DASHSCOPE_API_KEY else "",
    }


@router.post("/", response_model=Dict[str, Any])
async def update_settings(
    data: SettingsUpdate,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """更新配置并持久化到当前用户的 settings"""
    allowed_providers = {"deepseek", "openai", "anthropic", "ollama", "dashscope"}
    if data.default_provider is not None and data.default_provider not in allowed_providers:
        raise HTTPException(status_code=400, detail="不支持的模型服务商")

    saved = dict(user.settings) if isinstance(user.settings, dict) else {}
    updated = {}

    if data.default_provider is not None:
        saved["default_provider"] = data.default_provider
        updated["default_provider"] = data.default_provider

    if data.ollama_url is not None:
        saved["ollama_url"] = data.ollama_url
        updated["ollama_url"] = data.ollama_url

    if data.ollama_model is not None:
        saved["ollama_model"] = data.ollama_model
        updated["ollama_model"] = data.ollama_model

    # API Key 属于服务端环境配置，不接受通过该接口写入，避免明文落库
    user.settings = saved
    db.commit()

    return {
        "success": True,
        "updated": updated,
        "message": "配置已保存"
    }


@router.get("/providers", response_model=List[ProviderStatus])
async def get_provider_status(user: User = Depends(require_auth)):
    """检查各 LLM 提供商状态"""
    providers = []
    
    # 检查 DeepSeek (默认)
    deepseek_status = ProviderStatus(
        name="deepseek",
        display_name="DeepSeek",
        available=bool(settings.DEEPSEEK_API_KEY),
        models=["deepseek-chat", "deepseek-coder"],
        error=None if settings.DEEPSEEK_API_KEY else "未配置 API Key"
    )
    providers.append(deepseek_status)
    
    # 检查 OpenAI
    openai_status = ProviderStatus(
        name="openai",
        display_name="OpenAI",
        available=bool(settings.OPENAI_API_KEY),
        models=["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        error=None if settings.OPENAI_API_KEY else "未配置 API Key"
    )
    providers.append(openai_status)
    
    # 检查 Anthropic
    anthropic_status = ProviderStatus(
        name="anthropic",
        display_name="Claude",
        available=bool(settings.ANTHROPIC_API_KEY),
        models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        error=None if settings.ANTHROPIC_API_KEY else "未配置 API Key"
    )
    providers.append(anthropic_status)
    
    # 检查 Ollama (本地)
    ollama_available = False
    ollama_error = None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                ollama_available = True
    except Exception as e:
        ollama_error = f"连接失败: {str(e)}"
    
    # 获取 Ollama 可用模型
    ollama_models = []
    if ollama_available:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    ollama_models = [m.get("name", "unknown") for m in data.get("models", [])]
        except:
            pass
    
    ollama_status = ProviderStatus(
        name="ollama",
        display_name="Ollama (本地)",
        available=ollama_available,
        models=ollama_models if ollama_models else ["llama3", "llama2", "mistral"],
        error=ollama_error
    )
    providers.append(ollama_status)
    
    # 检查 DashScope
    dashscope_status = ProviderStatus(
        name="dashscope",
        display_name="阿里云通义千问",
        available=bool(settings.DASHSCOPE_API_KEY),
        models=["qwen-turbo", "qwen-plus", "qwen-max"],
        error=None if settings.DASHSCOPE_API_KEY else "未配置 API Key"
    )
    providers.append(dashscope_status)
    
    return providers


@router.get("/database", response_model=DatabaseStatus)
async def get_database_status(user: User = Depends(require_auth)):
    """检查数据库连接状态"""
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        # 事务状态检查
        try:
            result = db.execute(text("SELECT 1"))
            result.close()
        except Exception:
            db.rollback()
        
        # 执行简单查询检查连接
        result = db.execute(text("SELECT version()"))
        version = result.scalar()
        result.close()
        
        # 获取向量信息
        vectors_count = 0
        vector_dimension = 1024  # DashScope text-embedding-v3 默认维度，与 vectors.embedding 列一致
        
        # 检查 vectors 表
        try:
            result = db.execute(text("SELECT count(*) FROM vectors"))
            count = result.scalar()
            result.close()
            vectors_count = count if count else 0
        except Exception:
            pass
        
        # 获取数据库信息
        try:
            db_info_result = db.execute(text("SELECT current_database(), inet_server_addr(), inet_server_port()"))
            db_info = db_info_result.fetchone()
            db_info_result.close()
        except Exception:
            db_info = ("knowledge_assistant", "localhost", "5432")
        
        status_parts = [f"向量维度: {vector_dimension}"]
        if vectors_count > 0:
            status_parts.append(f"({vectors_count} 条向量)")
        status_parts.append("PostgreSQL 运行正常")
        
        return DatabaseStatus(
            connected=True,
            host=f"{db_info[1]}:{db_info[2]}" if db_info else "localhost",
            database=db_info[0] if db_info else "unknown",
            vector_dimension=vector_dimension,
            status=" | ".join(status_parts)
        )
    except Exception as e:
        print(f"数据库状态检查失败: {e}")
        return DatabaseStatus(
            connected=False,
            host="localhost:5432",
            database="knowledge_assistant",
            vector_dimension=0,
            status=f"连接失败: {str(e)[:100]}"
        )
    finally:
        db.close()
