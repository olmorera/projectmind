# projectmind/agents/agent_factory.py

from sqlalchemy.orm import Session
from projectmind.db.session import engine
from projectmind.db.models.agent import Agent as AgentModel
from projectmind.db.models.llm_config import LLMConfig
from projectmind.db.models.llm_model import LLMModel
from projectmind.llm.llama_provider import LlamaProvider
from projectmind.agents.base_agent import BaseAgent, AgentDefinition
from loguru import logger

class AgentFactory:
    @staticmethod
    def create(agent_name: str) -> BaseAgent:
        with Session(engine) as session:
            logger.info(f"🧠 Loading agent '{agent_name}' dynamically from database")

            # 1. Obtener el agente
            agent_row = session.query(AgentModel).filter_by(name=agent_name, is_active=True).first()
            if not agent_row:
                raise ValueError(f"Agent '{agent_name}' not found in database")

            # 2. Obtener configuración LLM
            config = session.query(LLMConfig).filter_by(id=agent_row.llm_config_id).first()
            if not config:
                raise ValueError(f"LLMConfig not found for agent '{agent_name}'")

            model = session.query(LLMModel).filter_by(id=config.llm_model_id).first()
            if not model:
                raise ValueError(f"LLMModel not found for agent '{agent_name}'")

            # 3. Instanciar LlamaProvider
            llm = LlamaProvider(config=config, model=model)

            # 4. Crear definición del agente
            definition = AgentDefinition(
                name=agent_row.name,
                role=agent_row.type,
                goal=agent_row.goal,
                type=agent_row.type,
            )

            return BaseAgent(definition=definition, llm=llm)
