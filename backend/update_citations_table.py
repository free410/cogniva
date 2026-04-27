"""
数据库迁移脚本：添加 Citation 表缺失的列
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from core.database import engine

def run_migration():
    """添加缺失的列到 citations 表"""
    
    columns_to_add = [
        ("intent_match_ratio", "FLOAT"),
        ("topic_match", "BOOLEAN"),
        ("entity_match_score", "FLOAT"),
        ("term_match_score", "FLOAT"),
        ("matched_entities", "JSON")
    ]
    
    with engine.connect() as conn:
        # 检查 citations 表是否存在
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename = 'citations'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print("citations 表不存在，跳过迁移")
            return
        
        print("检查并添加缺失的列...")
        
        for column_name, column_type in columns_to_add:
            try:
                # 检查列是否存在
                result = conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'citations' 
                    AND column_name = '{column_name}'
                """))
                
                if result.fetchone() is None:
                    # 列不存在，添加它
                    sql = f"ALTER TABLE citations ADD COLUMN {column_name} {column_type};"
                    conn.execute(text(sql))
                    print(f"  添加列: {column_name} ({column_type})")
                else:
                    print(f"  列已存在: {column_name}")
                    
            except Exception as e:
                print(f"  添加列 {column_name} 时出错: {e}")
                # 可能已经存在但检查失败，继续处理下一个
        
        conn.commit()
        print("\n迁移完成！")

if __name__ == "__main__":
    print("=" * 50)
    print("Citation 表数据库迁移")
    print("=" * 50)
    run_migration()
    print("按回车键退出...")
    input()