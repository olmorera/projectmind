from projectmind.agents.agent_factory import AgentFactory
from loguru import logger
import re

async def evaluate_effectiveness_score(system_prompt: str, user_input: str, response: str) -> int:
    if not response.strip():
        logger.warning("⚠️ Skipping evaluation: agent response is empty.")
        return 1  # peor puntaje posible

    agent = AgentFactory.create("prompt_evaluator")

    eval_prompt = (
        "You are an evaluator. Your job is to rate how well an AI agent's response fulfills the user request.\n\n"
        f"SYSTEM PROMPT:\n{system_prompt.strip()}\n\n"
        f"USER REQUEST:\n{user_input.strip()}\n\n"
        f"AGENT RESPONSE:\n{response.strip()}\n\n"
        "Please answer ONLY with a single number from 1 (terrible) to 10 (perfect).\n"
        "Do NOT add explanation. Do NOT repeat the input. Respond only with the number."
    )

    logger.debug("🧪 Evaluating effectiveness using prompt_evaluator...")
    score_raw = agent.run(eval_prompt).strip()
    logger.debug(f"🔢 Raw score response: {score_raw}")

    match = re.search(r"\b([1-9]|10)\b", score_raw)
    if match:
        score = int(match.group(1))
        logger.info(f"📊 Evaluator extracted score: {score}")
        return score
    else:
        logger.warning(f"⚠️ Could not parse evaluation score from: {score_raw}")
        return 1
