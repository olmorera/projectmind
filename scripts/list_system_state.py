# scripts/list_system_state.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from textwrap import shorten

from projectmind.db.models import Agent, Prompt, LLMModel, LLMConfig

load_dotenv()
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def list_state():
    async with AsyncSessionLocal() as session:
        print("\n🤖 Registered Agents:")
        result = await session.execute(Agent.__table__.select().order_by(Agent.name))
        agents = result.fetchall()
        for agent in agents:
            print(f"  - {agent.name} [{agent.type}] → llm_config_id: {agent.llm_config_id}")

        print("\n🧠 Active Prompts:")
        result = await session.execute(Prompt.__table__.select().where(Prompt.is_active == True).order_by(Prompt.agent_name, Prompt.version))
        prompts = result.fetchall()
        for prompt in prompts:
            short_text = shorten(prompt.prompt, width=60, placeholder="...")
            print(f"  - {prompt.agent_name} (v{prompt.version}) → {short_text}")

        print("\n🧩 LLM Configurations:")
        result = await session.execute(LLMConfig.__table__.select().order_by(LLMConfig.name))
        configs = result.fetchall()
        for config in configs:
            print(f"  - {config.name} (max_tokens={config.max_tokens}, temp={config.temperature}) → model_id: {config.llm_model_id}")

        print("\n📦 LLM Models:")
        result = await session.execute(LLMModel.__table__.select().order_by(LLMModel.name))
        models = result.fetchall()
        for model in models:
            print(f"  - {model.name} → {model.model}")

if __name__ == "__main__":
    asyncio.run(list_state())
