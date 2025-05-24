# projectmind/utils/prompt_optimizer.py

from loguru import logger
from projectmind.prompts.prompt_manager import PromptManager
from projectmind.agents.agent_factory import AgentFactory
from projectmind.utils.slack_notifier import notify_slack


async def maybe_optimize_prompt(agent_row, run_result: dict, score: int):
    logger.warning(f"⚠️ Low score ({score}) for agent '{agent_row.name}'. Optimizing prompt...")

    optimizer = AgentFactory.create("prompt_optimizer")
    optimization_prompt = (
        f"You are a senior prompt engineer optimizing prompts for AI agents.\n\n"
        f"--- Current Prompt ---\n{run_result['system_prompt']}\n\n"
        f"--- Agent Info ---\nName: {agent_row.name}\n\n"
        f"--- User Input ---\n{run_result['input']}\n\n"
        f"--- Model Output ---\n{run_result['output']}\n\n"
        f"--- Evaluation Score ---\n{score}\n\n"
        f"Your task is to rewrite the system prompt to better guide the model.\n"
        f"Return ONLY the improved prompt."
    )

    improved_prompt = optimizer.run(optimization_prompt)

    async with PromptManager.session_context() as session:
        manager = PromptManager(session)
        original_prompt = await manager.get_latest_prompt(agent_row.name, "default")
        new_prompt = await manager.register_prompt_version(original_prompt, improved_prompt)

        await notify_slack({
            "agent": agent_row.name,
            "prompt_id": str(original_prompt.id),
            "version_old": original_prompt.version,
            "version_new": new_prompt.version,
            "model_used": agent_row.model_name,
            "original": original_prompt.content,
            "improved": improved_prompt
        })
