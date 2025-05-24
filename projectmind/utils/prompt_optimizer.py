# projectmind/utils/prompt_optimizer.py

from loguru import logger
from projectmind.prompts.prompt_manager import PromptManager
from projectmind.utils.prompt_generator import improve_prompt
from projectmind.utils.agent_evaluator import evaluate_effectiveness_score


async def maybe_optimize_prompt(
    agent_row,
    prompt_manager: PromptManager,
    system_prompt: str,
    user_input: str,
    response: str,
):
    try:
        # Validación inicial del output del modelo
        if not response or not isinstance(response, str) or not response.strip():
            logger.warning(f"⚠️ Empty or invalid response for agent '{agent_row.name}', skipping optimization.")
            return

        # Obtener score de efectividad
        score = await evaluate_effectiveness_score(response, goal=agent_row.goal)
        if score is None:
            logger.warning(f"⚠️ Could not extract a valid score for agent '{agent_row.name}'")
            return

        logger.info(f"📊 Effectiveness score for '{agent_row.name}': {score}")
        await prompt_manager.update_effectiveness_score(agent_row.name, "default", score)

        if score >= 8:
            logger.info(f"✅ High effectiveness — no optimization needed for '{agent_row.name}'")
            return

        # Prompt base desde DB o fallback al proporcionado
        old_prompt = await prompt_manager.get_latest_prompt(agent_row.name, "default")
        base_prompt = old_prompt.prompt if old_prompt and old_prompt.prompt else system_prompt

        if not base_prompt or not base_prompt.strip():
            logger.warning(f"❌ No valid base prompt to improve for agent '{agent_row.name}'")
            return

        # Mejora del prompt
        improved_prompt = await improve_prompt(base_prompt, user_input, response, score, agent_row.name)

        if not improved_prompt or not improved_prompt.strip():
            logger.warning(f"❌ Skipped saving: Improved prompt is invalid for agent '{agent_row.name}'")
            return

        if old_prompt and old_prompt.prompt.strip() == improved_prompt.strip():
            logger.info(f"ℹ️ Skipped saving: Improved prompt is identical to current one for agent '{agent_row.name}'")
            return

        # Registrar nueva versión del prompt
        await prompt_manager.register_prompt_version(old_prompt, improved_prompt)
        logger.success(f"✨ Registered improved prompt for '{agent_row.name}' (score: {score})")

    except Exception as e:
        logger.error(f"❌ Failed to optimize prompt for '{agent_row.name}': {e}")
