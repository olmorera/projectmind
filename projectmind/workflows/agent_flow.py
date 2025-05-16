# agent_flow.py

import os
import uuid
from typing import Dict, Any

from dotenv import load_dotenv
from loguru import logger
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.runnables.base import RunnableLambda  # ✅ compatible

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from projectmind.agents.agent_factory import AgentFactory
from projectmind.db.models import AgentRun, Prompt
from projectmind.memory.memory_manager import MemoryManager

# Load environment variables
load_dotenv()

# --- DB URLs
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")

# --- DB setup (for async tasks like agents and memory)
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# --- Checkpointer (LangGraph state persistence with psycopg3)
with PostgresSaver.from_conn_string(SYNC_DATABASE_URL) as saver:
    saver.setup()
    checkpointer = saver

# --- Node execution
async def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_name = state.get("agent_name")
    input_text = state.get("input")
    user_id = state.get("slack_user", None)

    if not agent_name or not input_text:
        raise ValueError("Missing required keys: 'agent_name' and/or 'input' in state")

    logger.info(f"🤖 Executing agent: {agent_name}")
    logger.debug(f"📥 Input: {input_text}")

    async with AsyncSessionLocal() as session:
        # 1. Load agent
        agent = await AgentFactory.create(agent_name, session)

        # 2. Load prompt
        result = await session.execute(
            select(Prompt)
            .where(Prompt.agent_name == agent_name, Prompt.task_type == "generate", Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        prompt_obj = result.scalar_one_or_none()
        if not prompt_obj:
            raise ValueError(f"No active prompt found for agent '{agent_name}'")

        # 3. Load memory context
        memory = MemoryManager(namespace="task_outputs")
        memory_key = f"{agent_name}:last"
        context = await memory.get([memory_key], session)
        full_prompt = f"{context}\n\n{prompt_obj.prompt}\n\n{input_text}" if context else f"{prompt_obj.prompt}\n\n{input_text}"

        # 4. Run agent
        output = agent.run(full_prompt)

        # 5. Save result in memory (if valuable)
        await memory.set(memory_key, output, session)

        # 6. Store run
        run = AgentRun(
            id=uuid.uuid4(),
            agent_name=agent_name,
            user_id=user_id,
            input=input_text,
            output=output,
            extra={"context_used": bool(context)}
        )
        session.add(run)
        await session.commit()

        logger.success(f"✅ Agent run saved: {run.id}")

        return {
            **state,
            "output": output,
            "run_id": str(run.id)
        }

# --- Flow constructor
def agent_flow():
    workflow = StateGraph(dict)
    workflow.add_node("agent", RunnableLambda(lambda state: agent_node(state)))  # ✅ ejecuta async correctamente
    workflow.set_entry_point("agent")
    workflow.set_finish_point("agent")
    graph = workflow.compile()
    graph = graph.with_config({"checkpointer": checkpointer})
    return graph
