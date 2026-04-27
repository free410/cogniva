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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
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
                
    except Exception as e:
        print(f"Error during startup: {e}")
        import traceback
        traceback.print_exc()
        raise

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