"""
数据库迁移脚本 - 为 users 表添加 username 和 password_hash 字段
运行: python scripts/migrate_add_username.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine

def migrate():
    """添加 username 和 password_hash 字段到 users 表"""

    with engine.connect() as conn:
        # 检查 username 字段是否存在
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'username'
        """))
        has_username = result.fetchone() is not None

        if not has_username:
            print("添加 username 字段...")
            conn.execute(text("""
                ALTER TABLE users ADD COLUMN username VARCHAR(100) UNIQUE
            """))
            conn.commit()
            print("✅ username 字段添加成功")

            # 将现有的 email 复制到 username（如果没有的话）
            result = conn.execute(text("SELECT id, email FROM users WHERE username IS NULL"))
            for row in result:
                user_id, email = row
                # 使用 email 的 @ 前部分作为 username
                if email and '@' in email:
                    base_username = email.split('@')[0]
                else:
                    base_username = f"user_{str(user_id)[:8]}"
                conn.execute(text("UPDATE users SET username = :username WHERE id = :id"),
                           {"username": base_username, "id": str(user_id)})
            conn.commit()
            print("✅ 已将 email 前缀复制为 username")
        else:
            print("username 字段已存在")

        # 检查 password_hash 字段是否存在
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'password_hash'
        """))
        has_password_hash = result.fetchone() is not None

        if not has_password_hash:
            print("添加 password_hash 字段...")
            conn.execute(text("""
                ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)
            """))
            conn.commit()
            print("✅ password_hash 字段添加成功")
        else:
            print("password_hash 字段已存在")

    print("\n迁移完成！")

if __name__ == "__main__":
    migrate()
