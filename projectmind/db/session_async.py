# projectmind/db/session_async.py

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
if not ASYNC_DATABASE_URL or not ASYNC_DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise ValueError("ASYNC_DATABASE_URL must use 'postgresql+asyncpg://' for async support")

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
