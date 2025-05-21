# projectmind/utils/input_adapter.py

from langdetect import detect
from loguru import logger
from typing import Tuple

from projectmind.agents.agent_factory import AgentFactory

async def adapt_input_for_agent(input_text: str, agent_name: str) -> Tuple[str, str, bool]:
    """
    Detects language, translates if needed, and optimizes the prompt for the agent.
    Returns: (adapted_input, original_input, was_translated)
    """
    original_input = input_text
    lang = detect(input_text)
    was_translated = False

    if lang != "en":
        logger.info(f"🌐 Detected language '{lang}' — translating input for agent '{agent_name}'")

        translator = AgentFactory.create("translator")
        translation_prompt = (
            f"You are a professional translator and assistant.
             Translate and adapt the following request into clear, technical English, ready to be interpreted by an AI agent named '{agent_name}'.
             Maintain the intent and clarify ambiguities if needed.
             
             Original input:
             {input_text}"
        )

        input_text = translator.run(translation_prompt)
        was_translated = True

    return input_text.strip(), original_input.strip(), was_translated
