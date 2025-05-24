from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from projectmind.db.models.prompt import Prompt
from projectmind.utils.agent_evaluator import evaluate_effectiveness_score
from projectmind.agents.agent_factory import AgentFactory
from projectmind.utils.slack_notifier import notify_slack
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

    async def update_effectiveness_score(self, agent_name: str, task_type: str, score: int):
        result = await self.session.execute(
            select(Prompt)
            .where(Prompt.agent_name == agent_name)
            .where(Prompt.task_type == task_type)
            .where(Prompt.is_active == True)
        )
        prompt = result.scalar_one_or_none()
        if prompt:
            prompt.effectiveness_score = score
            await self.session.commit()
            logger.info(f"📌 Updated effectiveness score to {score} for '{agent_name}'")
        else:
            logger.warning(f"⚠️ Could not find active prompt to update score for '{agent_name}'")

    async def evaluate_and_optimize_if_needed(
        self, agent_row, system_prompt: str, user_input: str, response: str
    ):
        from projectmind.utils.prompt_optimizer import maybe_optimize_prompt
        from projectmind.utils.agent_evaluator import evaluate_effectiveness_score

        if not response.strip():
            logger.warning(f"⚠️ Skipping evaluation: no output was generated for agent '{agent_row.name}'")
            return

        score = await evaluate_effectiveness_score(system_prompt, user_input, response)
        await self.update_effectiveness_score(agent_row.name, "default", score)

        if score < 7 and agent_row.optimize_prompt:
            await maybe_optimize_prompt(agent_row, {
                "system_prompt": system_prompt,
                "input": user_input,
                "output": response
            }, score)


    async def maybe_optimize_prompt(self, agent_row, prompt_obj: Prompt, run_result: dict, score: int):
        logger.warning(f"⚠️ Score {score} is low, triggering optimization for '{agent_row.name}'")

        optimizer = AgentFactory.create("prompt_optimizer")
        optimization_prompt = (
            f"You are a senior prompt engineer optimizing prompts for AI agents.\n\n"
            f"--- Current Prompt ---\n{run_result['system_prompt']}\n\n"
            f"--- Agent ---\n{agent_row.name}\n\n"
            f"--- User Input ---\n{run_result['input']}\n\n"
            f"--- Model Output ---\n{run_result['output']}\n\n"
            f"--- Evaluation Score ---\n{score}\n\n"
            f"Your task is to rewrite the system prompt to better guide the model in generating relevant, complete, and safe output.\n"
            f"Return ONLY the improved prompt."
        )

        improved_prompt = optimizer.run(optimization_prompt)

        new_prompt = await self.register_prompt_version(prompt_obj, improved_prompt)

        await notify_slack({
            "agent": agent_row.name,
            "prompt_id": str(prompt_obj.id),
            "version_old": prompt_obj.version,
            "version_new": new_prompt.version,
            "model_used": agent_row.model_name,
            "original": prompt_obj.content,
            "improved": improved_prompt
        })
