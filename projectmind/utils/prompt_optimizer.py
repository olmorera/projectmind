import asyncio
import uuid
from sqlalchemy import select, update
from projectmind.db.models import Prompt, Agent
from projectmind.utils.prompt_generator import improve_prompt
from projectmind.utils.agent_evaluator import evaluate_effectiveness_score
from projectmind.db.session_async import AsyncSessionLocal
from loguru import logger

EFFECTIVENESS_THRESHOLD = 8

async def optimize_prompt_if_needed(agent_name: str, prompt: str, response: str):
    goal = await get_agent_goal(agent_name)
    score = await evaluate_effectiveness_score(response, goal=goal)
    logger.info(f"🎯 Effectiveness score: {score}/10")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Prompt)
            .where(Prompt.agent_name == agent_name)
            .where(Prompt.task_type == "default")
            .where(Prompt.is_active == True)
        )
        current_prompt = result.scalar_one_or_none()

        if not current_prompt:
            logger.warning(f"⚠️ No active prompt found for '{agent_name}'")
            return

        # Always update the current effectiveness score
        await session.execute(
            update(Prompt)
            .where(Prompt.id == current_prompt.id)
            .values(effectiveness_score=score)
        )

        if score >= EFFECTIVENESS_THRESHOLD:
            logger.success(f"✅ Prompt for '{agent_name}' is effective (score: {score})")
            await session.commit()
            return

        logger.warning(f"⚠️ Prompt for '{agent_name}' is suboptimal (score: {score}), improving...")
        improved_prompt = await improve_prompt(prompt)

        new_version = float(current_prompt.version) + 1.0
        new_prompt = Prompt(
            id=str(uuid.uuid4()),
            agent_name=agent_name,
            task_type="default",
            prompt=improved_prompt,
            is_active=True,
            version=new_version,
            effectiveness_score=0.0
        )

        current_prompt.is_active = False
        session.add(new_prompt)
        await session.commit()
        logger.success(f"🔁 Created improved prompt version {new_version:.1f} for '{agent_name}'")

async def get_agent_goal(agent_name: str) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Agent.goal).where(Agent.name == agent_name)
        )
        return result.scalar_one_or_none() or ""
