import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from sqlalchemy import text
from sqlalchemy.orm import Session
from core.database import engine

with Session(engine) as session:
    try:
        session.execute(text('ALTER TABLE citations ADD COLUMN IF NOT EXISTS reranker_score FLOAT'))
        session.execute(text('ALTER TABLE citations ADD COLUMN IF NOT EXISTS vector_score FLOAT'))
        session.execute(text('ALTER TABLE citations ADD COLUMN IF NOT EXISTS bm25_score FLOAT'))
        session.execute(text('ALTER TABLE citations ADD COLUMN IF NOT EXISTS keyword_score FLOAT'))
        session.execute(text('ALTER TABLE citations ADD COLUMN IF NOT EXISTS matched_terms JSON'))
        session.execute(text('ALTER TABLE citations ADD COLUMN IF NOT EXISTS rank INTEGER'))
        session.execute(text('ALTER TABLE citations ADD COLUMN IF NOT EXISTS chunk_content TEXT'))
        session.execute(text('ALTER TABLE citations ADD COLUMN IF NOT EXISTS chunk_index INTEGER'))
        session.commit()
        print('Database columns added successfully!')
    except Exception as e:
        session.rollback()
        print(f'Error: {e}')