"""
迁移脚本：为 chunks 表添加 metadata 列
用于支持切块策略等元数据存储

运行方式：python -m scripts.add_chunk_metadata
"""

import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine


def run_migration():
    """执行迁移"""
    print("开始迁移：为 chunks 表添加 metadata 列...")
    
    with engine.connect() as conn:
        # 检查列是否已存在
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'chunks' AND column_name = 'metadata'
        """))
        columns = result.fetchall()
        
        if columns:
            print("metadata 列已存在，跳过迁移")
            return True
        
        # 添加 metadata 列
        try:
            conn.execute(text("ALTER TABLE chunks ADD COLUMN metadata JSON DEFAULT '{}'"))
            conn.commit()
            print("metadata 列添加成功！")
            return True
        except Exception as e:
            print(f"添加列失败: {e}")
            return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
