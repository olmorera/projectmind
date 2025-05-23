# projectmind/llm/prompt_formatter.py

from typing import List, Dict


def format_prompt(prompt_base: str, user_input: str, chat_format: str) -> List[Dict[str, str]]:
    """
    Builds the structured list of messages to be sent to the LLM,
    based on the specified chat_format.

    Args:
        prompt_base (str): The base system prompt from the prompts table.
        user_input (str): The specific task or instruction.
        chat_format (str): The model's expected format (e.g. 'chatml', 'llama-2').

    Returns:
        List[Dict[str, str]]: Structured list of messages ready for LLM input.
    """

    if chat_format in ("chatml", "openchat", "zephyr", "mistral", "openhermes"):
        # Most chat-based formats use role-based inputs
        return [
            {"role": "system", "content": prompt_base},
            {"role": "user", "content": user_input}
        ]
    
    elif chat_format == "llama-2":
        # LLaMA 2 format uses special INST tags
        content = f"<<SYS>>\n{prompt_base}\n<</SYS>>\n\n{user_input}"
        return [
            {"role": "user", "content": f"[INST] {content} [/INST]"}
        ]
    
    elif chat_format == "phi-2":
        # PHI-2 doesn't support chat, send plain text
        return [
            {"role": "user", "content": f"{prompt_base}\n\n{user_input}"}
        ]
    
    elif chat_format == "none" or not chat_format:
        # No chat format, fallback to direct concatenation
        return [
            {"role": "user", "content": f"{prompt_base}\n\n{user_input}"}
        ]

    else:
        raise ValueError(f"Unsupported chat_format: {chat_format}")
