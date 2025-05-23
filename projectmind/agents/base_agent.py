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
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
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
            system_prompt = self.definition.system_prompt
            if not system_prompt or not isinstance(system_prompt, str):
                raise ValueError(f"❌ Invalid or missing system prompt for agent '{self.name}'")

            if not input or not isinstance(input, str):
                raise ValueError(f"❌ Invalid user input for agent '{self.name}'")

            messages = format_prompt(
                system_prompt=system_prompt.strip(),
                user_prompt=input.strip(),
                chat_format=self.llm.model.chat_format or "llama-2"
            )

            response = self.llm.chat(messages)
            logger.debug(f"✅ LLM response:\n{response}")
            return response

        except Exception as e:
            logger.error(f"❌ Error generating response for agent '{self.name}': {e}")
            return f"⚠️ Failed to generate response: {str(e)}"

    async def arun(self, input: str) -> str:
        from asyncio import to_thread
        return await to_thread(self.run, input)
