import os
import asyncio
import uuid
from dotenv import load_dotenv
from loguru import logger
from typing import Dict, Any

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from langgraph.graph import StateGraph

from projectmind.prompts.prompt_manager import PromptManager
from projectmind.agents.base_agent import AgentDefinition, BaseAgent
from projectmind.db.models.task import Task
from projectmind.db.models.planner_run import PlannerRun

load_dotenv()

# --- Configuración de DB ---
engine = create_async_engine(os.getenv("POSTGRES_URL"), echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# --- Nodo Planner ---
async def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("🔧 Running planner node...")
    logger.debug(f"🔎 Incoming state: {state}")

    user_input = state.get("input")
    if not user_input:
        raise ValueError("Missing 'input' in state")

    slack_user = state.get("slack_user", None)

    async with AsyncSessionLocal() as session:
        # Obtener prompt y preparar agente
        prompt_manager = PromptManager(session)
        prompt_text = await prompt_manager.get_latest_prompt(agent_type="planner")

        agent = BaseAgent(AgentDefinition(
            name="Planner",
            role="Plans a project",
            goal="Break down user input into actionable tasks",
            type="planner"
        ))

        full_prompt = f"{prompt_text}\n\nUser input: {user_input}"
        agent_result = agent.run(prompt=full_prompt)

        # Simulación de tareas (esto se reemplazará con LLM real)
        simulated_tasks = [
            "Define the data model for book rentals",
            "Create a PostgreSQL schema",
            "Develop backend API for books and users",
            "Build frontend UI for book browsing",
            "Implement login and user roles",
        ]

        created_task_ids = []
        for description in simulated_tasks:
            task = Task(
                id=uuid.uuid4(),
                description=description,
                status="pending"
            )
            session.add(task)
            created_task_ids.append(str(task.id))

        # Registrar ejecución del planner
        planner_run = PlannerRun(
            user_id=slack_user,
            input_prompt=user_input,
            output_response=agent_result,
            task_ids=created_task_ids
        )
        session.add(planner_run)

        await session.commit()
        logger.info(f"📌 Planner run recorded: {planner_run.id}")

        return {
            **state,
            "planner_output": agent_result,
            "task_ids": created_task_ids,
            "planner_run_id": str(planner_run.id)
        }

# --- Grafo LangGraph ---
def planner_flow():
    workflow = StateGraph(dict)
    workflow.add_node("planner", planner_node)
    workflow.set_entry_point("planner")
    workflow.set_finish_point("planner")
    return workflow.compile()
