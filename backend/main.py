import sys
import io

# Windows控制台UTF-8编码设置
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import Base, engine
from api import documents_router, chat_router, memory_router, search_router
from api.auth import router as auth_router, get_current_user
from api.settings import router as settings_router
from models import User

app = FastAPI(
    title="Cogniva API",
    description="智能知识问答平台 API",
    version="1.0.0"
)

# CORS 配置
_cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["http://localhost:3000"],
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(settings_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(search_router)


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    try:
        from core.database import Base, engine
        from models import User
        from sqlalchemy.orm import Session
        from sqlalchemy import text

        # 确保 pgvector 扩展可用（已启用时跳过，避免无谓的 schema 变更）
        with engine.connect() as conn:
            has_vector = conn.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            ).scalar()
            if not has_vector:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()

        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")

        # 常用查询索引（幂等创建，避免外键过滤全表扫描）
        with engine.connect() as conn:
            for stmt in (
                "CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents (user_id)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id)",
                "CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id)",
                "CREATE INDEX IF NOT EXISTS idx_citations_message_id ON citations (message_id)",
                "CREATE INDEX IF NOT EXISTS idx_citations_chunk_id ON citations (chunk_id)",
                "CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks (document_id)",
                "CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories (user_id)",
            ):
                conn.execute(text(stmt))
            conn.commit()

        if not settings.APP_SECRET or settings.APP_SECRET.startswith("default"):
            print("WARNING: APP_SECRET 使用默认值，生产环境请在 .env 中配置随机密钥")
        
        # 创建默认用户
        with Session(engine) as session:
            from models import User
            existing_user = session.query(User).filter(User.username == "admin").first()
            if not existing_user:
                default_user = User(
                    username="admin",
                    email="admin@local",
                    name="Administrator",
                    settings={},
                    password_hash=None  # 初始无密码，后续可通过注册接口设置
                )
                session.add(default_user)
                session.commit()
                print("Default user created: admin")
            else:
                print("Default user already exists: admin")

        # 后台预热重排模型，避免首次检索时等待模型加载
        def _warm_reranker():
            try:
                from core.database import SessionLocal
                from services.rag_service import RAGService
                db = SessionLocal()
                try:
                    RAGService(db).reranker
                finally:
                    db.close()
            except Exception as e:
                print(f"Reranker warmup failed: {e}")

        import threading
        threading.Thread(target=_warm_reranker, daemon=True).start()

    except Exception as e:
        print(f"Error during startup: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.get("/health")
async def health():
    """容器健康检查"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {
        "message": "Cogniva API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)