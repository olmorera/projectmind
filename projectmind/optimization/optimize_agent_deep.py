import asyncio
from loguru import logger
from sqlalchemy import select
from contextlib import asynccontextmanager

from projectmind.db.session_async import get_async_session
from projectmind.db.models.agent import Agent
from projectmind.utils.agent_runner import run_agent_once
from projectmind.utils.prompt_optimizer import optimize_prompt_if_needed, improve_prompt
from projectmind.utils.agent_evaluator import evaluate_effectiveness_score
from projectmind.prompts.prompt_manager import PromptManager

MAX_ATTEMPTS = 10
PASSING_SCORE = 4  # o ajusta a 8 si es del 1 al 10

@asynccontextmanager
async def session_context():
    async for session in get_async_session():
        yield session

async def optimize_agent(agent_name: str, test_input: str):
    logger.info(f"🔍 Starting deep optimization for agent: {agent_name}")

    async with session_context() as session:
        manager = PromptManager(session)

        for attempt in range(1, MAX_ATTEMPTS + 1):
            logger.info(f"⚙️ Attempt {attempt}/{MAX_ATTEMPTS} for '{agent_name}'")
            try:
                result = await run_agent_once(agent_name, test_input=test_input, return_full_info=True)
                response = result.get("output")
                prompt = result.get("prompt_used")
                goal = result.get("goal")

                if not response or not goal:
                    logger.warning(f"⚠️ Skipping attempt due to missing response or goal. Response: {response}, Goal: {goal}")
                    continue

                logger.debug(f"📤 Prompt used: {prompt}")
                logger.debug(f"📥 Response received: {response}")

                score = await evaluate_effectiveness_score(response, goal=goal)
                logger.info(f"📊 Effectiveness score: {score}")

                # 🧠 Actualizamos el score en la tabla prompts
                await manager.update_effectiveness_score(agent_name, "default", score)

                if score >= PASSING_SCORE:
                    logger.success(f"✅ High-quality prompt for '{agent_name}', stopping optimization.")
                    break
                else:
                    old_prompt = await manager.get_latest_prompt(agent_name, "default")
                    improved = await improve_prompt(prompt)
                    await manager.register_prompt_version(old_prompt, improved)
                    logger.info(f"✨ Improved prompt registered for agent '{agent_name}'")

            except Exception as e:
                logger.error(f"❌ Error optimizing '{agent_name}' on attempt {attempt}", exc_info=True)


async def main():
    async with session_context() as session:
        result = await session.execute(
            select(Agent.name, Agent.test_input).where(Agent.is_active == True)
        )
        agents = result.fetchall()

    logger.info(f"🔁 Optimizing {len(agents)} agents...")

    for name, test_input in agents:
        if not test_input:
            logger.warning(f"⚠️ Skipping '{name}' — no test_input defined.")
            continue
        await optimize_agent(name, test_input)

if __name__ == "__main__":
    asyncio.run(main())
