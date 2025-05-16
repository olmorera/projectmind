# projectmind/prompts/prompt_manager.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from projectmind.db.models.prompt import Prompt
from loguru import logger

class PromptManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_prompt(self, agent_type: str) -> str:
        stmt = (
            select(Prompt)
            .where(Prompt.agent_type == agent_type)
            .where(Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        prompt = result.scalar_one_or_none()
        if prompt:
            logger.debug(f"Loaded prompt for agent_type '{agent_type}' version {prompt.version}")
            return prompt.content
        else:
            raise ValueError(f"No prompt found for agent_type: {agent_type}")

    async def register_prompt(self, agent_type: str, content: str, version: int = 1):
        prompt = Prompt(agent_type=agent_type, content=content, version=version)
        self.session.add(prompt)
        await self.session.commit()
        logger.info(f"Registered new prompt for agent_type '{agent_type}' v{version}")
