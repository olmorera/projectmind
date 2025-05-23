from projectmind.agents.agent_factory import AgentFactory
from loguru import logger

async def improve_prompt(original_prompt: str) -> str:
    agent = AgentFactory.create("prompt_optimizer")
    logger.debug(f"🔧 Improving prompt: {original_prompt}")
    result = await agent.arun(original_prompt)
    return result.strip()
