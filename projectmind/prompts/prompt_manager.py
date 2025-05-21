# projectmind/prompts/prompt_manager.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from projectmind.db.models.prompt import Prompt
from loguru import logger


class PromptManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_prompt_by_id(self, prompt_id: str) -> Prompt:
        result = await self.session.execute(select(Prompt).where(Prompt.id == prompt_id))
        prompt = result.scalar_one_or_none()
        if not prompt:
            raise ValueError(f"Prompt with id {prompt_id} not found")
        return prompt

    async def get_latest_prompt(self, agent_name: str, task_type: str) -> Prompt:
        stmt = (
            select(Prompt)
            .where(Prompt.agent_name == agent_name)
            .where(Prompt.task_type == task_type)
            .where(Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        prompt = result.scalar_one_or_none()
        if not prompt:
            raise ValueError(f"No active prompt found for agent '{agent_name}' and task '{task_type}'")
        logger.debug(f"🔁 Loaded prompt for '{agent_name}' v{prompt.version}")
        return prompt

    async def register_prompt_version(self, old_prompt: Prompt, new_content: str) -> Prompt:
        new_prompt = Prompt(
            agent_name=old_prompt.agent_name,
            task_type=old_prompt.task_type,
            version=old_prompt.version + 1,
            content=new_content,
            is_active=True
        )
        old_prompt.is_active = False
        self.session.add(new_prompt)
        await self.session.commit()
        logger.info(f"🔄 New version for '{old_prompt.agent_name}' -> v{new_prompt.version}")
        return new_prompt
