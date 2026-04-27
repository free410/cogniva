"""添加 evidence 字段到 messages 表"""
import sys
sys.path.insert(0, '.')

from core.database import engine, Base
from sqlalchemy import text
import uuid

def migrate():
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'messages' AND column_name = 'evidence'
        """))
        
        if result.fetchone():
            print("字段 'evidence' 已存在，跳过")
            return
        
        # 添加 evidence 字段（JSON类型）
        conn.execute(text("""
            ALTER TABLE messages ADD COLUMN evidence JSON;
        """))
        conn.commit()
        print("成功添加 'evidence' 字段到 messages 表")

if __name__ == "__main__":
    migrate()
