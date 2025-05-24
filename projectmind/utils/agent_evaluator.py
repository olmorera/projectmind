# projectmind/utils/agent_evaluator.py

from loguru import logger
from sqlalchemy import select
from projectmind.db.session_async import get_async_session
from projectmind.db.models.agent import Agent
from projectmind.agents.agent_factory import create
from projectmind.llm.llama_provider import LlamaProvider

# Este modelo debe ser lo más ligero posible y mantener buena calidad
EVALUATOR_AGENT_NAME = "prompt_evaluator"

async def evaluate_effectiveness_score(response: str, goal: str) -> float:
    logger.debug("🧪 Evaluating effectiveness using prompt_evaluator...")

    try:
        # Carga el agente desde la base
        async for session in get_async_session():
            result = await session.execute(select(Agent).where(Agent.name == EVALUATOR_AGENT_NAME))
            agent_row = result.scalar_one_or_none()

            if not agent_row:
                logger.warning(f"⚠️ Agent '{EVALUATOR_AGENT_NAME}' not found.")
                return 1.0

            model = LlamaProvider(agent_row.model_name)
            agent = create(agent_row, model)

            agent_input = (
                f"You are an evaluator. Your job is to rate how well an AI agent's response fulfills the user request.\n\n"
                f"SYSTEM PROMPT:\n{goal.strip()}\n\n"
                f"USER REQUEST:\n{goal.strip()}\n\n"
                f"AGENT RESPONSE:\n{response.strip()}\n\n"
                f"Please answer ONLY with a single number from 1 (terrible) to 10 (perfect).\n"
                f"Do NOT add explanation. Do NOT repeat the input. Respond only with the number."
            )

            raw = await agent.arun(agent_input)
            logger.debug(f"🔢 Raw score response: {raw}")

            # Extrae número válido del string
            digits = "".join(filter(str.isdigit, raw))
            score = int(digits) if digits else 1
            return max(1, min(score, 10))

    except Exception as e:
        logger.warning(f"⚠️ Evaluation failed: {e}")
        return 1.0
