from projectmind.agents.agent_factory import AgentFactory
from loguru import logger
import re

async def evaluate_effectiveness_score(response: str, goal: str) -> int:
    """
    Uses the 'prompt_evaluator' agent to evaluate how well a response fulfills a goal.
    Returns a score from 1 to 10.
    """
    agent = AgentFactory.create("prompt_evaluator")

    eval_prompt = (
        "You are an evaluator. Your job is to rate how well an AI agent's response fulfills the given goal.\n\n"
        f"GOAL:\n{goal.strip()}\n\n"
        f"RESPONSE:\n{response.strip()}\n\n"
        "Please answer ONLY with a single number from 1 (terrible) to 10 (perfect).\n"
        "Do NOT add explanation. Do NOT repeat the goal or response. Respond only with the number."
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
        return 1  # fallback mínimo
