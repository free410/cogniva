"""
设置默认管理员用户密码
运行: python scripts/init_admin.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine, Base
from models import User
from core.auth import get_password_hash

def init_admin_user():
    """为默认 admin 用户设置密码"""

    # 创建表（如果不存在）
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 查找 admin 用户
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            print("用户 'admin' 不存在，正在创建...")
            admin = User(
                username="admin",
                email="admin@local",
                name="Administrator",
                settings={}
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("✅ 已创建 admin 用户")

        # 设置密码
        password = input("请输入 admin 用户的新密码 (至少6个字符): ").strip()

        if len(password) < 6:
            print("密码长度不足6个字符")
            return

        # 更新密码
        admin.password_hash = get_password_hash(password)
        db.commit()

        print(f"✅ 成功为用户 '{admin.username}' 设置新密码")
        print(f"   用户名: {admin.username}")
        print(f"   邮箱: {admin.email}")

    except Exception as e:
        print(f"错误: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_admin_user()
