import asyncio
import os
from dotenv import load_dotenv
load_dotenv('.env')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Chunk, Vector

engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)
db = Session()

chunks = db.query(Chunk).join(Vector).all()
print(f'Total chunks: {len(chunks)}')

for i, chunk in enumerate(chunks):
    print(f'\n=== Chunk {i+1} ===')
    print(f'ID: {chunk.id}')
    print(f'Document ID: {chunk.document_id}')
    print(f'Content preview: {chunk.content[:150]}...' if len(chunk.content) > 150 else f'Content: {chunk.content}')
    print(f'Chunk index: {chunk.chunk_index}')

db.close()