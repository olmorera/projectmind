import asyncio
from loguru import logger
from projectmind.agents.agent_factory import AgentFactory

async def run_agent_once(agent_name: str, input: str, return_full_info: bool = False):
    """
    Runs the specified agent once with the given input and optionally returns full info.
    """
    agent = AgentFactory.create(agent_name)
    logger.debug(f"🧠 Running agent '{agent_name}' with input: {input}")
    output = agent.run(input)

    if return_full_info:
        return {
            "system_prompt": agent.system_prompt.strip(),
            "input": input.strip(),
            "output": output.strip() if output else ""
        }
    return output.strip() if output else ""
