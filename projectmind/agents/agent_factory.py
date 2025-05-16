# projectmind/agents/agent_factory.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from projectmind.db.models.agent import Agent as AgentModel
from projectmind.agents.base_agent import BaseAgent, AgentDefinition
from loguru import logger

class AgentFactory:
    @staticmethod
    async def create(name: str, session: AsyncSession) -> BaseAgent:
        """
        Dynamically loads an agent definition from the database
        and returns a configured BaseAgent instance.
        """
        stmt = select(AgentModel).where(AgentModel.name == name, AgentModel.is_active == True)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            raise ValueError(f"No active agent found with name '{name}'")

        logger.info(f"🧠 Loading agent '{name}' dynamically from database")

        agent_def = AgentDefinition(
            name=row.name,
            role=row.type,
            goal=row.goal,
            type=row.type
        )

        agent = BaseAgent(agent_def)

        # Runtime config (model, temp, memory)
        agent.config.model = row.model
        agent.config.temperature = row.temperature
        agent.config.use_memory = row.use_memory

        return agent
