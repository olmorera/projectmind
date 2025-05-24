# projectmind/agents/agent_factory.py

from projectmind.agents.base_agent import BaseAgent
from projectmind.llm.llama_provider import LlamaProvider
from projectmind.db.session import get_session

def create(agent_name: str) -> BaseAgent:
    """
    Crea y devuelve un agente basado en el nombre proporcionado.
    """
    # Crear una sesión para obtener los detalles del agente
    session = get_session()
    agent_row = session.query(BaseAgent).filter(BaseAgent.name == agent_name).first()

    if not agent_row:
        raise ValueError(f"Agent '{agent_name}' not found in database.")

    # Aquí, según el nombre del agente, se carga el modelo respectivo.
    model = LlamaProvider(agent_row.model_name)  # Asumiendo que 'model_name' está en la base de datos

    # Asumimos que BaseAgent tiene la capacidad de aceptar un modelo de LlamaProvider
    return BaseAgent(agent_row.name, model)
