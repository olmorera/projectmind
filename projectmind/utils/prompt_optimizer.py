from loguru import logger
from projectmind.agents.agent_factory import AgentFactory
from projectmind.prompts.prompt_manager import PromptManager
from projectmind.utils.slack_notifier import notify_slack


async def maybe_optimize_prompt(session, agent_row, agent, prompt_obj, output):
    if not agent_row.optimize_prompt:
        return

    lines = output.strip().splitlines()
    unique_ratio = len(set(lines)) / max(len(lines), 1)

    if not output or len(output.strip()) < 50 or unique_ratio < 0.5:
        optimizer = AgentFactory.create("prompt_optimizer")
        feedback = "Output was empty, too short, or repetitive"
        optimization_prompt = (
            f"You are an expert in prompt optimization.\n\n"
            f"Original prompt:\n{prompt_obj.prompt}\n\n"
            f"Feedback:\n{feedback}\n\n"
            f"Please rewrite the prompt to improve clarity, usefulness, and effectiveness without changing its intent."
        )
        improved = optimizer.run(optimization_prompt)
        manager = PromptManager(session)
        new_prompt = await manager.register_prompt_version(prompt_obj, improved)

        await notify_slack({
            "agent": agent.name,
            "prompt_id": str(prompt_obj.id),
            "version_old": prompt_obj.version,
            "version_new": new_prompt.version,
            "model_used": agent.llm.model.name,
            "original": prompt_obj.prompt,
            "improved": improved
        })
