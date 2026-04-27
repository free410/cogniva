"""测试密码验证"""
from core.auth import verify_password, get_password_hash
from core.database import engine
from sqlalchemy import text

# 从数据库获取 testuser 的密码哈希
with engine.connect() as conn:
    result = conn.execute(text('SELECT password_hash FROM users WHERE username = :username'), {'username': 'testuser'})
    row = result.fetchone()
    if row:
        stored_hash = row[0]
        print(f'Stored hash: {stored_hash}')
        print(f'Verify 123456: {verify_password("123456", stored_hash)}')

# 生成新哈希测试
print('\nGenerating new hash...')
new_hash = get_password_hash('123456')
print(f'New hash: {new_hash}')
print(f'Verify new hash: {verify_password("123456", new_hash)}')
