from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/knowledge_assistant"
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DASHSCOPE_API_KEY: Optional[str] = None
    
    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # App settings
    APP_SECRET: str = "default-secret-key-change-in-production"
    DEBUG: bool = True
    
    # Upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # RAG settings - 优化切块策略
    CHUNK_SIZE: int = 1200        # 块大小（字符数）- 增大以保持内容完整
    CHUNK_OVERLAP: int = 200     # 块间重叠（字符数）- 增大以保持上下文连贯
    CHUNK_STRATEGY: str = "smart_hybrid"  # 切块策略：smart_hybrid(推荐), intent, entity, deep_semantic, recursive, semantic, markdown, sliding_window, hybrid
    TOP_K: int = 15             # 检索返回数量 - 减少到15确保高相关性
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()