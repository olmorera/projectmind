# scripts/register_default_agents.py

import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv
import os

from projectmind.db.models.agent import Agent

load_dotenv()

engine = create_async_engine(os.getenv("POSTGRES_URL"), echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)

AGENTS = [
    {
        "name": "planner",
        "type": "planner",
        "goal": "Break down project ideas into clear tasks",
        "model": "openai/gpt-4",
        "temperature": 0.2,
        "use_memory": True
    },
    {
        "name": "frontend_generator",
        "type": "generator",
        "goal": "Generate frontend code based on given tasks",
        "model": "openai/gpt-4",
        "temperature": 0.3,
        "use_memory": False
    },
    {
        "name": "backend_generator",
        "type": "generator",
        "goal": "Generate Supabase infrastructure from project requirements",
        "model": "openai/gpt-4",
        "temperature": 0.3,
        "use_memory": False
    }
]

async def main():
    async with Session() as session:
        for config in AGENTS:
            exists = await session.execute(
                select(Agent).where(Agent.name == config["name"])
            )
            if exists.scalar_one_or_none():
                print(f"⚠️ Agent '{config['name']}' already exists. Skipping.")
                continue

            agent = Agent(
                id=uuid.uuid4(),
                name=config["name"],
                type=config["type"],
                goal=config["goal"],
                model=config["model"],
                temperature=config["temperature"],
                use_memory=config["use_memory"],
                is_active=True
            )
            session.add(agent)

        await session.commit()
        print("✅ Default agents registered successfully.")

if __name__ == "__main__":
    asyncio.run(main())
