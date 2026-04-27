import os
from dotenv import load_dotenv
load_dotenv('.env')
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # 检查 pgvector 是否可用
    result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
    row = result.fetchone()
    print('pgvector extension:', 'installed' if row else 'NOT installed')
    
    # 检查一个向量的格式
    result2 = conn.execute(text('SELECT embedding FROM vectors LIMIT 1'))
    row2 = result2.fetchone()
    if row2:
        emb = row2[0]
        print('Sample vector type:', type(emb))
        print('Sample vector length:', len(str(emb)))
        print('Sample vector (first 100 chars):', str(emb)[:100])
