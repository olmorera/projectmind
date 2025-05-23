# projectmind/agents/base_agent.py

from pydantic import BaseModel, Field
from loguru import logger
from typing import Optional
from projectmind.llm.llama_provider import LlamaProvider
from projectmind.llm.prompt_formatter import format_prompt

class AgentDefinition(BaseModel):
    name: str
    role: str
    goal: str
    type: str
    prompt: Optional[str] = None
    test_input: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class BaseAgent:
    def __init__(self, definition: AgentDefinition, llm: LlamaProvider):
        self.definition = definition
        self.llm = llm
        logger.info(f"✅ Initialized agent '{definition.name}' of type '{definition.type}'")

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def goal(self) -> str:
        return self.definition.goal

    @property
    def agent_type(self) -> str:
        return self.definition.type

    def run(self, input: str) -> str:
        logger.debug(f"🧠 Agent '{self.name}' received input:\n{input}")

        try:
            messages = format_prompt(
                prompt_base=self.definition.prompt or "",
                user_input=input,
                chat_format=self.llm.model.chat_format or "llama-2"
            )

            response = self.llm.chat(messages)
            logger.debug(f"✅ LLM response:\n{response}")
            return response

        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return f"⚠️ Failed to generate response: {str(e)}"
