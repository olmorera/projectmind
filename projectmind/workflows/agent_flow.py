# projectmind/workflows/agent_flow.py

import os
import uuid
import re
from typing import Dict, Any

from dotenv import load_dotenv
from loguru import logger
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.runnables import RunnableLambda
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from projectmind.agents.agent_factory import AgentFactory
from projectmind.db.models import AgentRun, Prompt, Agent
from projectmind.memory.memory_manager import MemoryManager
from projectmind.prompts.prompt_manager import PromptManager
from projectmind.utils.language_utils import translate_to_english
from projectmind.workflows.slack_notifier import notify_slack
from projectmind.tasks.task_manager import save_tasks_from_output
from projectmind.db.crud.project import get_project_by_name, create_project  # Import CRUD proyectos

# 🔁 Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

with PostgresSaver.from_conn_string(DATABASE_URL) as saver:
    saver.setup()
    checkpointer = saver


async def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_name = state.get("agent_name")
    user_input = state.get("input")
    project_name = state.get("project_name")  # Aquí el cambio
    slack_user = state.get("slack_user", None)

    if not agent_name or user_input is None:
        raise ValueError("Missing 'agent_name' and/or 'input' in state")

    logger.info(f"🤖 Executing agent: {agent_name}")
    logger.debug(f"📥 Input: {user_input}")

    async with AsyncSessionLocal() as session:
        # Buscar o crear proyecto por nombre
        project = None
        if project_name:
            project = await get_project_by_name(session, project_name)
            if not project:
                # Usamos uuid4 para el id
                new_project_id = str(uuid.uuid4())
                project = await create_project(session, new_project_id, name=project_name)

        agent = AgentFactory.create(agent_name)

        # Detect and translate input if needed
        translated_input, was_translated = translate_to_english(user_input)

        if was_translated:
            logger.info("🌍 Input was not in English — translated before execution")
            await notify_slack({
                "agent": agent_name,
                "note": "User input was auto-translated to English before execution.",
                "original_input": user_input,
                "translated_input": translated_input
            })
        else:
            translated_input = user_input

        result = await session.execute(
            select(Prompt)
            .where(Prompt.agent_name == agent_name, Prompt.task_type == "default", Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        prompt_obj = result.scalar_one_or_none()
        if not prompt_obj:
            raise ValueError(f"No active prompt found for agent '{agent_name}'")

        agent_config = await session.execute(
            select(Agent).where(Agent.name == agent_name)
        )
        agent_row = agent_config.scalar_one()

        memory = MemoryManager(namespace="task_outputs")
        context = ""

        if project and agent.definition.type and agent_row.use_memory:
            context_items = await memory.get_project_context(
                project_id=project.id,
                agent_name=agent_name,
                task_type=agent.definition.type,
                session=session
            )
            context = "\n\n".join(context_items) if context_items else ""
            logger.debug(f"📚 Retrieved {len(context_items)} context items from memory for project {project_name}")
        else:
            logger.debug("📭 No project or agent type — skipping contextual memory.")

        use_context = len(context.strip()) > 10
        full_prompt = f"{context}\n\n{prompt_obj.prompt}\n\n{translated_input}" if use_context else f"{prompt_obj.prompt}\n\n{translated_input}"

        output = agent.run(full_prompt)

        # Guarda la memoria del proyecto si corresponde
        if project and agent.definition.type and agent_row.use_memory:
            try:
                await memory.save_project_context(
                    project_id=project.id,
                    agent_name=agent_name,
                    task_type=agent.definition.type,
                    content=output,
                    session=session
                )
                logger.success(f"🧠 Project memory stored for {agent_name}:{agent.definition.type} in project {project_name}")
            except Exception as e:
                logger.error(f"❌ Error saving project memory: {e}")
        else:
            if not project:
                logger.debug("ℹ️ No project provided — skipping memory storage.")
            if not agent.definition.type:
                logger.warning(f"⚠️ Agent '{agent_name}' has no type defined — skipping memory storage.")

        # Guarda las tareas en la base de datos SOLO si el agente tiene permiso
        if project and agent_row.can_create_tasks:
            try:
                await save_tasks_from_output(project.id, agent_name, output, session)
                logger.success(f"📝 Tasks saved for project {project_name} by agent {agent_name}")
            except Exception as e:
                logger.error(f"❌ Error saving tasks: {e}")

        run = AgentRun(
            id=uuid.uuid4(),
            agent_name=agent_name,
            user_id=slack_user,
            input=user_input,
            output=output,
            extra={
                "context_used": bool(use_context),
                "project_name": project.name if project else None,
                "was_translated": was_translated,
                "translated_input": translated_input if was_translated else None
            },
            llm_config_id=agent.llm.config.id
        )
        session.add(run)
        await session.commit()
        logger.success(f"✅ Agent run saved: {run.id}")

        if agent_row.optimize_prompt:
            output_lines = output.strip().splitlines()
            output_unique = len(set(output_lines))
            should_optimize = (
                not output or
                len(output.strip()) < 50 or
                output_unique < (len(output_lines) * 0.5)
            )

            if should_optimize:
                logger.warning(f"⚠️ Output from agent '{agent_name}' is weak — triggering prompt_optimizer")
                feedback = "Output was empty, too short, or repetitive"

                optimizer = AgentFactory.create("prompt_optimizer")
                optimization_prompt = (
                    f"You are an expert in prompt optimization.\n\n"
                    f"Original prompt:\n{prompt_obj.prompt}\n\n"
                    f"Feedback:\n{feedback}\n\n"
                    f"Please rewrite the prompt to improve clarity, usefulness, and effectiveness without changing its intent."
                )
                improved_prompt = optimizer.run(optimization_prompt)

                manager = PromptManager(session)
                new_prompt = await manager.register_prompt_version(prompt_obj, improved_prompt)

                await notify_slack({
                    "agent": agent_name,
                    "prompt_id": str(prompt_obj.id),
                    "version_old": prompt_obj.version,
                    "version_new": new_prompt.version,
                    "model_used": agent.llm.model.name,
                    "original": prompt_obj.prompt,
                    "improved": improved_prompt
                })
        else:
            logger.info(f"⚪ Optimization skipped for agent '{agent_name}' — optimize_prompt = False")
            await notify_slack({
                "agent": agent_name,
                "prompt_id": str(prompt_obj.id),
                "version_old": prompt_obj.version,
                "version_new": prompt_obj.version,
                "model_used": agent.llm.model.name,
                "original": prompt_obj.prompt,
                "improved": None,
                "note": "Prompt optimization skipped: optimize_prompt is disabled for this agent."
            })

        return {
            **state,
            "output": output,
            "run_id": str(run.id)
        }


def agent_flow():
    workflow = StateGraph(dict)
    workflow.add_node("agent", RunnableLambda(agent_node))

    def router(state: Dict[str, Any]):
        return "agent"

    workflow.set_conditional_entry_point(router)
    workflow.set_finish_point("agent")
    return workflow.compile().with_config({"checkpointer": checkpointer})
