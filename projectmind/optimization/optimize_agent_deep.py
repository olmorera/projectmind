import asyncio
from loguru import logger
from sqlalchemy import select
from contextlib import asynccontextmanager

from projectmind.db.session_async import get_async_session
from projectmind.db.models.agent import Agent
from projectmind.utils.agent_runner import run_agent_once
from projectmind.utils.prompt_optimizer import optimize_prompt_if_needed
from projectmind.utils.agent_evaluator import is_prompt_successful

MAX_ATTEMPTS = 10  # Número máximo de ciclos de optimización por agente

@asynccontextmanager
async def session_context():
    async for session in get_async_session():
        yield session

async def optimize_agent(agent_name: str):
    logger.info(f"🔍 Starting deep optimization for agent: {agent_name}")

    for attempt in range(MAX_ATTEMPTS):
        logger.info(f"⚙️ Attempt {attempt + 1}/{MAX_ATTEMPTS} for '{agent_name}'")

        try:
            result = await run_agent_once(agent_name, return_full_info=True)

            prompt = result.get("prompt")
            response = result.get("response")

            logger.debug(f"📤 Prompt used:{prompt}")
            logger.debug(f"📥 Response received:{response}")

            if is_prompt_successful(response):
                logger.success(f"✅ Prompt is successful for '{agent_name}' on attempt {attempt + 1}")
                break
            else:
                logger.warning(f"⚠️ Prompt failed or suboptimal for '{agent_name}', optimizing...")
                await optimize_prompt_if_needed(agent_name, prompt=prompt, response=response)

        except Exception as e:
            logger.exception(f"❌ Error optimizing '{agent_name}' on attempt {attempt + 1}")
            break

async def main():
    async with session_context() as session:
        result = await session.execute(select(Agent.name).where(Agent.is_active == True))
        agent_names = [row[0] for row in result.fetchall()]

    logger.info(f"🔁 Optimizing {len(agent_names)} agents...")
    for name in agent_names:
        await optimize_agent(name)

if __name__ == "__main__":
    asyncio.run(main())
