# utils/db.py
import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    conn = await asyncpg.connect(os.getenv("POSTGRES_URL"))
    result = await conn.fetch("SELECT 1;")
    print(result)
    await conn.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
