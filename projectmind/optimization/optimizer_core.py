# projectmind/optimization/optimizer_core.py

import uuid
from loguru import logger
from sqlalchemy import select
from projectmind.db.models import AgentRun, Prompt
from projectmind.prompts.prompt_manager import PromptManager
from projectmind.agents.agent_factory import AgentFactory
from projectmind.utils.slack_notifier import notify_slack
from projectmind.db.session_async import AsyncSessionLocal  # ✅ USO CORRECTO

def is_output_weak(output: str) -> bool:
    if not output or len(output.strip()) < 50:
        return True
    lines = output.strip().splitlines()
    return len(set(lines)) < (len(lines) * 0.5)

def calculate_effectiveness(output: str) -> float:
    if not output or len(output.strip()) < 30:
        return 0.0
    unique_lines = len(set(output.strip().splitlines()))
    total_lines = len(output.strip().splitlines())
    return round(unique_lines / total_lines, 3)

async def optimize_agent_prompt_and_config(agent_row):
    agent = AgentFactory.create(agent_row.name)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Prompt)
            .where(Prompt.agent_name == agent.name, Prompt.task_type == "default", Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        prompt_obj = result.scalar_one_or_none()
        if not prompt_obj:
            logger.warning(f"⚠️ No active prompt for agent {agent.name}")
            return

        prompt_text = prompt_obj.prompt
        output = agent.run(prompt_text)
        effectiveness = calculate_effectiveness(output)

        run = AgentRun(
            id=uuid.uuid4(),
            agent_name=agent.name,
            input="[prompt optimization]",
            output=output,
            llm_config_id=agent.llm.config.id,
            extra={
                "prompt_id": str(prompt_obj.id),
                "prompt_version": prompt_obj.version,
                "effectiveness_score": effectiveness,
                "config_used": {
                    "temperature": agent.llm.config.temperature,
                    "top_p": agent.llm.config.top_p,
                    "stop_tokens": agent.llm.config.stop_tokens,
                },
                "config_was_override": False
            }
        )
        session.add(run)

        if is_output_weak(output) and agent_row.optimize_prompt:
            optimizer = AgentFactory.create("prompt_optimizer")
            reason = "Output was too short or repetitive."
            optimization_prompt = (
                f"You are a senior prompt engineer optimizing prompts for AI agents.\n\n"
                f"--- Prompt (v{prompt_obj.version}) ---\n{prompt_text}\n\n"
                f"--- Agent context ---\n"
                f"Agent name: {agent.name}\n"
                f"Agent goal: {agent_row.goal}\n"
                f"Agent type: {agent.definition.type}\n"
                f"Model: {agent.llm.model.name}\n\n"
                f"--- Evaluation feedback ---\n"
                f"The output was weak due to: {reason}\n"
                f"Score: {effectiveness}\n\n"
                f"--- Your task ---\n"
                f"Rewrite the prompt to improve its clarity, precision, and effectiveness.\n"
                f"Keep the same intent, but make it more actionable and useful for the model.\n"
                f"Return only the improved prompt.\n"
            )

            improved_prompt = optimizer.run(optimization_prompt)

            manager = PromptManager(session)
            new_prompt = await manager.register_prompt_version(prompt_obj, improved_prompt)

            await notify_slack({
                "agent": agent.name,
                "prompt_id": str(prompt_obj.id),
                "version_old": prompt_obj.version,
                "version_new": new_prompt.version,
                "model_used": agent.llm.model.name,
                "original": prompt_text,
                "improved": improved_prompt
            })

        await session.commit()
        logger.success(f"✅ Optimization run completed for {agent.name}")
