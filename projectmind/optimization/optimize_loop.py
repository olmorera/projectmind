import asyncio
from loguru import logger
from sqlalchemy import select
from projectmind.db.session_async import AsyncSessionLocal
from projectmind.db.models.agent import Agent
from projectmind.optimization.optimizer_core import optimize_agent_prompt_and_config

SEMAPHORE = asyncio.Semaphore(1)

async def run_loop():
    logger.info("🔁 Starting continuous optimization loop...")
    while True:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Agent).where(Agent.optimize_prompt == True))
            agents = result.scalars().all()

        for agent_row in agents:
            try:
                async with SEMAPHORE:
                    await optimize_agent_prompt_and_config(agent_row)
            except Exception as e:
                logger.error(f"❌ Failed to optimize {agent_row.name}: {e}")

        logger.info("⏳ Waiting 15 minutes until next optimization cycle...")
        await asyncio.sleep(900)  # 15 minutes

if __name__ == "__main__":
    asyncio.run(run_loop())
