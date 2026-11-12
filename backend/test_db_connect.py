import os

import psycopg2
from psycopg2 import sql

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "postgres")
    )
    conn.set_session(autocommit=True)  # 设置自动提交
    cur = conn.cursor()
    
    # 检查 knowledge_assistant 数据库是否存在
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'knowledge_assistant'")
    exists = cur.fetchone()
    
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier('knowledge_assistant')))
        print('Created database: knowledge_assistant')
    else:
        print('Database knowledge_assistant already exists')
    
    conn.close()
    print('Done!')
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()