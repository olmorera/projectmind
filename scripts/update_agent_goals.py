import asyncio
from sqlalchemy import select
from projectmind.db.session_async import AsyncSessionLocal
from projectmind.db.models.agent import Agent
from loguru import logger

# Definición clara de objetivos por agente
agent_goals = {
    "planner": "Generate a structured list of technical tasks based on a user's goal or request.",
    "frontend_generator": "Generate grouped frontend code using Svelte and TailwindCSS, based on a task list.",
    "prompt_optimizer": "Improve existing prompts based on feedback and the intended goal of the target agent.",
    "backend_generator": "Generate Supabase schema, tables, RLS policies, and backend logic from task descriptions."
}

async def update_agent_goals():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Agent))
        agents = result.scalars().all()
        for agent in agents:
            if agent.name in agent_goals:
                old_goal = agent.goal
                agent.goal = agent_goals[agent.name]
                logger.info(f"🧠 Updated goal for {agent.name}:")
                logger.info(f"   OLD: {old_goal}")
                logger.info(f"   NEW: {agent.goal}")
                session.add(agent)
        await session.commit()
        logger.success("✅ Agent goals updated successfully")

if __name__ == "__main__":
    asyncio.run(update_agent_goals())
