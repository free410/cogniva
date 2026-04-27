import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='postgres',
        dbname='postgres'
    )
    print('Connected successfully!')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
