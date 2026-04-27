import asyncio
import os
from dotenv import load_dotenv
load_dotenv('.env')
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Chunk, Vector

engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)
db = Session()

# 1. 直接查询 chunks 和 vectors
print('=== Testing direct query ===')
chunks = db.query(Chunk).join(Vector).all()
print(f'Found {len(chunks)} chunks with vectors')

for chunk in chunks:
    print(f'  Chunk {chunk.id}: content length={len(chunk.content)}')
    if chunk.vector:
        emb = chunk.vector.embedding
        print(f'    Vector: type={type(emb)}, length={len(emb) if hasattr(emb, "__len__") else "N/A"}')
        print(f'    Vector sample: {emb[:5] if emb and len(emb) >= 5 else emb}')

# 2. 测试 cosine similarity
print('\n=== Testing cosine similarity ===')
from services.rag_service import embedding_service

query = '桃蚜的防治方法'
query_emb = embedding_service.embed([query])[0]
print(f'Query embedding sample: {query_emb[:5]}')

for chunk in chunks:
    if chunk.vector and chunk.vector.embedding:
        import numpy as np
        v1 = np.array(query_emb)
        v2 = np.array(chunk.vector.embedding)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 > 0 and norm2 > 0:
            sim = np.dot(v1, v2) / (norm1 * norm2)
            print(f'  Chunk {chunk.id}: similarity={sim:.4f}')

db.close()