# agent_flow.py

import os
import asyncio
from typing import Dict, Any

from dotenv import load_dotenv
from loguru import logger
from langgraph.graph import StateGraph

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from projectmind.agents.agent_factory import AgentFactory
from projectmind.db.models import AgentRun, Prompt

load_dotenv()

# --- DB setup
engine = create_async_engine(os.getenv("POSTGRES_URL"), echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

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
        # 1. Load agent from DB
        agent = await AgentFactory.create(agent_name, session)

        # 2. Load prompt dynamically
        result = await session.execute(
            select(Prompt)
            .where(Prompt.agent_name == agent_name, Prompt.task_type == "default", Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        prompt_obj = result.scalar_one_or_none()

        if not prompt_obj:
            raise ValueError(f"No active prompt found for agent '{agent_name}'")

        full_prompt = f"{prompt_obj.prompt}\n\n{input_text}"

        # 3. Run agent
        output = agent.run(full_prompt)

        # 4. Store result
        run = AgentRun(
            agent_name=agent_name,
            user_id=user_id,
            input=input_text,
            output=output,
            extra=state.get("extra")
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
    workflow.add_node("agent", agent_node)
    workflow.set_entry_point("agent")
    workflow.set_finish_point("agent")
    return workflow.compile()
