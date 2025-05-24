# projectmind/prompts/prompt_manager.py

from loguru import logger
from sqlalchemy import select
from projectmind.db.models.prompt import Prompt

class PromptManager:
    def __init__(self, session):
        self.session = session

    async def get_latest_prompt(self, agent_name: str, task_type: str = "default") -> Prompt:
        result = await self.session.execute(
            select(Prompt)
            .where(Prompt.agent_name == agent_name, Prompt.task_type == task_type, Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        prompt = result.scalar_one_or_none()

        if not prompt:
            logger.error(f"❌ No active prompt found for agent '{agent_name}' with task type '{task_type}'")
            raise ValueError(f"No active prompt found for agent '{agent_name}' with task type '{task_type}'")

        if not prompt.system_prompt or not isinstance(prompt.system_prompt, str) or not prompt.system_prompt.strip():
            logger.error(f"❌ Retrieved prompt for agent '{agent_name}' is empty or invalid")
            raise ValueError(f"Prompt for agent '{agent_name}' is empty or invalid")

        return prompt

    async def update_effectiveness_score(self, agent_name: str, task_type: str, score: float):
        try:
            prompt = await self.get_latest_prompt(agent_name, task_type)
            prompt.effectiveness_score = score
            self.session.add(prompt)
            await self.session.commit()
            logger.info(f"📌 Updated effectiveness score to {score} for '{agent_name}'")
        except Exception as e:
            logger.warning(f"⚠️ Failed to update effectiveness score for '{agent_name}': {e}")

    async def register_prompt_version(self, old_prompt: Prompt, new_text: str):
        from projectmind.db.models.prompt import Prompt  # evitar ciclos

        new_version = str(float(old_prompt.version) + 1.0)
        new_prompt = Prompt(
            agent_name=old_prompt.agent_name,
            task_type=old_prompt.task_type,
            version=new_version,
            system_prompt=new_text,
            is_active=True
        )
        old_prompt.is_active = False
        self.session.add_all([old_prompt, new_prompt])
        await self.session.commit()
        logger.info(f"✅ Registered new prompt version for '{old_prompt.agent_name}' → v{new_version}")

    async def evaluate_and_optimize_if_needed(self, agent_row, system_prompt: str, user_prompt: str, response: str):
        from projectmind.utils.prompt_optimizer import maybe_optimize_prompt
        from projectmind.utils.agent_evaluator import evaluate_effectiveness_score

        try:
            score = await evaluate_effectiveness_score(system_prompt, user_prompt, response)
            logger.info(f"📊 Evaluated effectiveness score: {score}")
            await self.update_effectiveness_score(agent_row.name, "default", score)

            if score < 8:
                await maybe_optimize_prompt(
                    agent_row=agent_row,
                    prompt_manager=self,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response=response,
                )
        except Exception as e:
            logger.warning(f"⚠️ Prompt optimization failed for '{agent_row.name}': {e}")
