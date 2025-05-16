# projectmind/agents/base_agent.py

from pydantic import BaseModel
from loguru import logger
from typing import Optional, Literal

class AgentDefinition(BaseModel):
    name: str
    role: str
    goal: str
    type: Literal["planner", "frontend_generator", "backend_generator"]
    metadata: Optional[dict] = {}

class BaseAgent:
    def __init__(self, config: AgentDefinition):
        self.config = config
        logger.info(f"Initialized agent '{config.name}' as {config.type}")

    def run(self, prompt: str) -> str:
        logger.debug(f"Agent '{self.config.name}' received prompt: {prompt}")
        return f"Response from {self.config.name} (not implemented yet)."
