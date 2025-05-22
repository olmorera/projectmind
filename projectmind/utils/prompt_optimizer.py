from loguru import logger
from projectmind.db.session_async import get_async_session
from projectmind.db.models.prompt import Prompt
from sqlalchemy import select, update
from uuid import uuid4

def is_prompt_successful(response: str) -> bool:
    """
    Determines if the agent's response is considered successful.

    Success criteria (can evolve):
    - Response is not empty or whitespace.
    - Does not contain only repeated or meaningless tokens.
    - Length is reasonable to assume a valid response.

    Returns:
        bool: True if the response is useful.
    """
    if not response or not response.strip():
        return False

    stripped = response.strip().lower()
    too_short = len(stripped) < 10
    too_repetitive = stripped.count('.') > len(stripped) * 0.5

    return not too_short and not too_repetitive


async def improve_prompt(old_prompt: str, response: str) -> str:
    """
    Generates a better version of the prompt based on the response.
    You can evolve this function to use a prompt-tuning model or scoring logic.

    Args:
        old_prompt (str): The original prompt.
        response (str): The suboptimal or failed response.

    Returns:
        str: A new improved version of the prompt.
    """
    if "evaluate" in old_prompt.lower():
        return old_prompt.replace("Evaluate", "Thoroughly analyze")
    elif "generate" in old_prompt.lower():
        return old_prompt.replace("Generate", "Generate a better version of")
    else:
        # Fallback heuristic
        return f"Improve the following request:\n{old_prompt.strip()}"


async def optimize_prompt_if_needed(agent_name: str, prompt: str, response: str) -> None:
    """
    Checks if a prompt needs improvement and registers a new version if necessary.

    Args:
        agent_name (str): The agent's name.
        prompt (str): The prompt to optimize.
        response (str): The agent's response to evaluate.
    """
    if is_prompt_successful(response):
        logger.info(f"✅ Prompt for '{agent_name}' was actually successful, no optimization needed.")
        return

    logger.warning(f"⚠️ Optimizing prompt for agent '{agent_name}' due to suboptimal response.")

    new_prompt = await improve_prompt(prompt, response)

    async for session in get_async_session():
        # Find current active prompt
        current = await session.execute(
            select(Prompt).filter_by(agent_name=agent_name, is_active=True)
        )
        current_prompt = current.scalar_one_or_none()

        if current_prompt:
            current_prompt.is_active = False
            logger.info(f"🔄 Deactivating previous prompt v{current_prompt.version} for agent '{agent_name}'")

        # Register new improved prompt
        version = str(round(float(current_prompt.version) + 1.0, 1)) if current_prompt else "1.0"

        new_entry = Prompt(
            id=str(uuid4()),
            agent_name=agent_name,
            content=new_prompt.strip(),
            version=version,
            is_active=True,
        )
        session.add(new_entry)
        await session.commit()
        logger.success(f"✨ Registered new prompt v{version} for '{agent_name}'")
