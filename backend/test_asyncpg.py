import asyncio
import asyncpg

async def test_db():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            user='postgres',
            password='postgres',
            database='postgres'
        )
        print('Connected successfully!')
        await conn.close()
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(test_db())
