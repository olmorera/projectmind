# scripts/reset_llm_and_agents.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
import os

from projectmind.db.models import (
    AgentRun, Prompt, Agent, LLMConfig, LLMModel
)

load_dotenv()
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def reset_all():
    async with AsyncSessionLocal() as session:
        print("🧹 Cleaning agent_runs, prompts, agents, llm_configs, llm_models...")

        await session.execute(text("DELETE FROM agent_runs"))
        await session.execute(text("DELETE FROM prompts"))
        await session.execute(text("DELETE FROM agents"))
        await session.execute(text("DELETE FROM llm_configs"))
        await session.execute(text("DELETE FROM llm_models"))

        await session.commit()
        print("✅ All LLM-related tables cleaned.")

if __name__ == "__main__":
    asyncio.run(reset_all())
