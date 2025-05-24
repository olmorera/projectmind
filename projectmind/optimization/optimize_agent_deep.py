import asyncio
from loguru import logger
from sqlalchemy import select
from contextlib import asynccontextmanager

from projectmind.db.session_async import get_async_session
from projectmind.db.models.agent import Agent
from projectmind.utils.agent_runner import run_agent_once
from projectmind.utils.prompt_optimizer import improve_prompt
from projectmind.utils.agent_evaluator import evaluate_effectiveness_score
from projectmind.prompts.prompt_manager import PromptManager

MAX_ATTEMPTS = 1
PASSING_SCORE = 8  # 1–10 scale

@asynccontextmanager
async def session_context():
    async for session in get_async_session():
        yield session

async def optimize_agent(agent_name: str, user_prompt: str):
    logger.info(f"🔍 Starting deep optimization for agent: {agent_name}")

    async with session_context() as session:
        manager = PromptManager(session)

        for attempt in range(1, MAX_ATTEMPTS + 1):
            logger.info(f"⚙️ Attempt {attempt}/{MAX_ATTEMPTS} for '{agent_name}'")

            try:
                result = await run_agent_once(agent_name, user_prompt, return_full_info=True)
                response = result.get("response")
                system_prompt = result.get("system_prompt")
                #user_prompt = result.get("input")

                if not response or not user_prompt:
                    logger.warning(f"⚠️ Skipping attempt due to missing response or user prompt. Response: {response}, Prompt: {user_prompt}")
                    continue

                logger.debug(f"📤 System Prompt: {system_prompt}")
                logger.debug(f"📤 User Prompt: {user_prompt}")
                logger.debug(f"📥 Response received: {response}")

                # 🧪 Evaluate score
                score = await evaluate_effectiveness_score(system_prompt, user_prompt, response)
                logger.info(f"📊 Effectiveness score: {score}")

                # 💾 Update effectiveness score in prompt table
                await manager.update_effectiveness_score(agent_name, "default", score)

                if score >= PASSING_SCORE:
                    logger.success(f"✅ High-quality prompt for '{agent_name}', stopping optimization.")
                    break

                # ✨ Improve and version prompt
                old_prompt = await manager.get_latest_prompt(agent_name, "default")
                improved = await improve_prompt(system_prompt)
                await manager.register_prompt_version(old_prompt, improved)
                logger.info(f"🧠 Improved prompt registered for agent '{agent_name}'")

            except Exception as e:
                logger.exception(f"🔥 Error optimizing '{agent_name}' on attempt {attempt}")
                continue

async def main():
    async with session_context() as session:
        result = await session.execute(
            select(Agent.name, Agent.user_prompt).where(Agent.is_active == True)
        )
        agents = result.fetchall()

    logger.info(f"🔁 Optimizing {len(agents)} agents...")

    for name, user_prompt in agents:
        if not user_prompt:
            logger.warning(f"⚠️ Skipping '{name}' — no user_prompt defined.")
            continue
        await optimize_agent(name, user_prompt=user_prompt)

if __name__ == "__main__":
    asyncio.run(main())
