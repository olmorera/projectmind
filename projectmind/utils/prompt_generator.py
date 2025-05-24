# projectmind/utils/prompt_generator.py

from loguru import logger
from sqlalchemy import select
from projectmind.db.session_async import get_async_session
from projectmind.db.models.agent import Agent
from projectmind.agents.agent_factory import create
from projectmind.llm.llama_provider import LlamaProvider


async def improve_prompt(
    original_prompt: str,
    user_input: str,
    response: str,
    score: float,
    agent_name: str,
) -> str:
    """
    Uses the prompt_optimizer agent to improve the original system prompt
    given the user input, the response generated, and its low effectiveness score.
    """

    prompt_optimizer_name = "prompt_optimizer"

    async for session in get_async_session():
        result = await session.execute(select(Agent).where(Agent.name == prompt_optimizer_name))
        agent_row = result.scalar_one_or_none()

        if not agent_row:
            raise ValueError(f"⚠️ Agent '{prompt_optimizer_name}' not found in database.")

        model = LlamaProvider(agent_row.model_name)
        agent = create(agent_row, model)

        logger.debug(f"🔧 Improving prompt for '{agent_name}' (score: {score})")

        # Construir input estructurado
        improvement_input = (
            f"You are an expert prompt engineer.\n"
            f"Your job is to improve the SYSTEM PROMPT used by an AI agent.\n\n"
            f"---\nOriginal SYSTEM PROMPT:\n{original_prompt.strip()}\n\n"
            f"---\nUSER INPUT:\n{user_input.strip()}\n\n"
            f"---\nAGENT RESPONSE:\n{response.strip()}\n\n"
            f"---\nEFFECTIVENESS SCORE: {score}\n\n"
            f"Now, improve the SYSTEM PROMPT to help the agent respond better next time.\n"
            f"Return only the improved prompt. Do not add explanations or formatting."
        )

        improved_prompt = await agent.arun(improvement_input)
        return improved_prompt.strip()
