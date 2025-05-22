import asyncio
from loguru import logger
from sqlalchemy import select
from projectmind.db.session_async import AsyncSessionLocal
from projectmind.db.models import Agent
from projectmind.optimization.optimizer_core import optimize_agent_prompt_and_config

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Agent).where(Agent.optimize_prompt == True))
        agents = result.scalars().all()

    for agent_row in agents:
        try:
            await optimize_agent_prompt_and_config(agent_row)
        except Exception as e:
            logger.error(f"❌ Failed to optimize {agent_row.name}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
