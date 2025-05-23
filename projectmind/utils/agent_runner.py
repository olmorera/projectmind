# projectmind/utils/agent_runner.py

from projectmind.agents.agent_factory import AgentFactory
from loguru import logger
from typing import Optional


async def run_agent_once(agent_name: str, test_input: Optional[str] = None, return_full_info: bool = False):
    """
    Run an agent once using the given name and test input.

    Args:
        agent_name (str): The name of the agent to load.
        test_input (str, optional): The input to pass to the agent for testing.
        return_full_info (bool): Whether to return additional details.

    Returns:
        If return_full_info is False, returns only the agent output.
        If True, returns a dict with output, prompt_used, agent_type, and goal.
    """
    logger.info(f"🚀 Running agent '{agent_name}' for deep evaluation")

    agent = AgentFactory.create(agent_name)
    logger.debug(f"🧠 Input for agent '{agent_name}':\n{test_input or ''}")

    output = agent.run(test_input or "")
    logger.debug(f"✅ Output from '{agent_name}': {output}")

    if return_full_info:
        return {
            "output": output,
            "prompt_used": agent.definition.prompt,
            "agent_type": agent.definition.type,
            "goal": agent.definition.goal,
        }

    return output
