# scripts/register_default_prompts.py

import asyncio
import uuid
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

from projectmind.db.models.prompt import Prompt

load_dotenv()

engine = create_async_engine(os.getenv("POSTGRES_URL"), echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)

PROMPTS = [
    {
        "agent_name": "planner",
        "task_type": "default",
        "version": "1.0",
        "prompt": (
            "You are a project planning agent. Your goal is to analyze a user prompt "
            "and return a list of clear, detailed, and actionable tasks needed to build the requested system. "
            "Be logical, organized, and include any infrastructure or configuration requirements the system might need."
        )
    },
    {
        "agent_name": "frontend_generator",
        "task_type": "default",
        "version": "1.0",
        "prompt": (
            "You are a frontend code generator agent. Based on a list of tasks and system goals, "
            "you must generate clean, responsive, and accessible UI code using the specified frontend framework. "
            "Include routing, protected pages, SEO tags, and secure integration with backend endpoints. "
            "Use TailwindCSS and modular components."
        )
    },
    {
        "agent_name": "backend_generator",
        "task_type": "default",
        "version": "1.0",
        "prompt": (
            "You are a backend infrastructure generator. Your job is to generate all necessary SQL scripts and Supabase configurations "
            "based on the project requirements. This includes:\n"
            "- PostgreSQL table definitions with indexes and relationships\n"
            "- RLS policies ensuring strict access control by user_id or organization\n"
            "- Supabase Storage buckets with proper CORS and access restrictions\n"
            "- Custom Supabase Functions or RPCs if needed\n"
            "Make everything optimized, modular, and secure by default."
        )
    }
]

async def main():
    async with Session() as session:
        for config in PROMPTS:
            prompt = Prompt(
                id=uuid.uuid4(),
                agent_name=config["agent_name"],
                task_type=config["task_type"],
                version=config["version"],
                prompt=config["prompt"]
            )
            session.add(prompt)

        await session.commit()
        print("✅ Default prompts registered successfully.")

if __name__ == "__main__":
    asyncio.run(main())
