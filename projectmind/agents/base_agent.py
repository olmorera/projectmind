# projectmind/agents/base_agent.py

from pydantic import BaseModel, Field
from loguru import logger
from typing import Optional, Literal

class AgentDefinition(BaseModel):
    name: str
    role: str
    goal: str
    type: Literal["planner", "frontend_generator", "backend_generator", "validator"]
    prompt: Optional[str] = None  # ✅ Ya no se requiere al crear
    metadata: dict = Field(default_factory=dict)  # ✅ evita usar {}

class BaseAgent:
    def __init__(self, definition: AgentDefinition):
        self.definition = definition
        self.config = type("Config", (), {})()  # Objeto dinámico
        logger.info(f"✅ Initialized agent '{definition.name}' of type '{definition.type}'")

    def run(self, prompt: str) -> str:
        logger.debug(f"🧠 Agent '{self.definition.name}' received prompt:\n{prompt}")
        return f"🛠 Agent '{self.definition.name}' executed. (Response generation not implemented yet.)"
