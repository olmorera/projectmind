# projectmind/utils/agent_runner.py

from loguru import logger
from projectmind.agents.agent_factory import AgentFactory

async def run_agent_once(agent_name: str, input: str = None, return_full_info: bool = False):
    logger.info(f"🚀 Running agent '{agent_name}' for evaluation")

    agent = AgentFactory.create(agent_name)
    result = agent.run(input or "Evaluate agent '{}' with a test prompt.".format(agent_name))

    if isinstance(result, dict):
        output = result.get("output", "")
        prompt = result.get("prompt", "")
    else:
        output = result
        prompt = ""

    logger.debug(f"🔎 Output: {output}")

    if return_full_info:
        return {
            "prompt": prompt,
            "response": output,
            "raw_output": output,
            "agent_name": agent_name,
        }

    return output
