# projectmind/agents/base_agent.py

from pydantic import BaseModel, Field
from loguru import logger
from typing import Optional, Literal
from projectmind.llm.llama_provider import LlamaProvider

class AgentDefinition(BaseModel):
    name: str
    role: str
    goal: str
    type: str
    prompt: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class BaseAgent:
    def __init__(self, definition: AgentDefinition, llm: LlamaProvider):
        self.definition = definition
        self.llm = llm  # LlamaProvider instance
        self.config = type("Config", (), {})()
        logger.info(f"✅ Initialized agent '{definition.name}' of type '{definition.type}'")

    def run(self, prompt: str) -> str:
        logger.debug(f"🧠 Agent '{self.definition.name}' received prompt:\n{prompt}")
        try:
            response = self.llm.generate(prompt)
            logger.debug(f"✅ Agent '{self.definition.name}' LLM output:\n{response}")
            return response
        except Exception as e:
            logger.error(f"❌ Error while generating response: {e}")
            return f"⚠️ Failed to generate response: {str(e)}"
