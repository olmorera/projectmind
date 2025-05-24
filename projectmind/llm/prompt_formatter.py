# projectmind/llm/prompt_formatter.py

from typing import List, Dict

def format_prompt(
    system_prompt: str,
    user_prompt: str,
    chat_format: str,
    chat_template: str | None = None
) -> List[Dict[str, str]]:
    """
    Builds the structured list of messages to be sent to the LLM,
    relying on the model's tokenizer.chat_template for formatting.

    Args:
        system_prompt (str): The base system prompt.
        user_prompt (str): The specific user task or query.
        chat_format (str): The declared format of the model.
        chat_template (Optional[str]): Optional raw template string from GGUF metadata.

    Returns:
        List[Dict[str, str]]: Structured message list for LLM chat input.
    """
    system_prompt = system_prompt.strip()
    user_prompt = user_prompt.strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
