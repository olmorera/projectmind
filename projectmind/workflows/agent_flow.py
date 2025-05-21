# projectmind/workflows/agent_flow.py

import os
import uuid
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
from projectmind.workflows.slack_notifier import notify_slack

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
    input_text = state.get("input")
    user_id = state.get("slack_user", None)

    if not agent_name or input_text is None:
        raise ValueError("Missing 'agent_name' and/or 'input' in state")

    logger.info(f"🤖 Executing agent: {agent_name}")
    logger.debug(f"📅 Input: {input_text}")

    async with AsyncSessionLocal() as session:
        agent = AgentFactory.create(agent_name)

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
        memory_key = f"{agent_name}:last"
        context = await memory.get([memory_key], session)

        use_context = len(input_text.strip()) > 10
        full_prompt = f"{context}\n\n{prompt_obj.prompt}\n\n{input_text}" if use_context and context else f"{prompt_obj.prompt}\n\n{input_text}"

        output = agent.run(full_prompt)
        await memory.set(memory_key, output, session)

        run = AgentRun(
            id=uuid.uuid4(),
            agent_name=agent_name,
            user_id=user_id,
            input=input_text,
            output=output,
            extra={"context_used": bool(context)},
            llm_config_id=agent.llm.config.id
        )
        session.add(run)
        await session.commit()
        logger.success(f"✅ Agent run saved: {run.id}")

        # 🚨 Verificar si se debe optimizar
        output_lines = output.strip().splitlines()
        output_unique = len(set(output_lines))
        should_optimize = (
            not output or
            len(output.strip()) < 50 or
            output_unique < (len(output_lines) * 0.5)
        )

        if agent_row.optimize_prompt:
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


async def prompt_optimizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    input_data = state.get("input", {})
    user_id = state.get("slack_user", None)

    prompt_id = input_data.get("prompt_id")
    success = input_data.get("success", True)
    feedback = input_data.get("feedback", "")
    model_used = input_data.get("model_used", "unknown")

    if not prompt_id:
        raise ValueError("Missing 'prompt_id' in input")

    async with AsyncSessionLocal() as session:
        manager = PromptManager(session)
        old_prompt = await manager.get_prompt_by_id(prompt_id)

        if success:
            logger.info(f"✅ Prompt {prompt_id} marked as successful — no optimization needed.")
            return {**state, "output": "Prompt was successful. No optimization performed."}

        agent = AgentFactory.create("prompt_optimizer")
        optimization_prompt = (
            f"You are an expert in prompt optimization.\n\n"
            f"Original prompt:\n{old_prompt.prompt}\n\n"
            f"Feedback:\n{feedback}\n\n"
            f"Model used: {model_used}\n\n"
            f"Please rewrite the prompt to improve clarity, usefulness, and effectiveness."
        )
        improved = agent.run(optimization_prompt)

        new_prompt = await manager.register_prompt_version(old_prompt, improved)

        run = AgentRun(
            id=uuid.uuid4(),
            agent_name="prompt_optimizer",
            user_id=user_id,
            input=input_data,
            output=improved,
            extra={"optimized_from": str(old_prompt.id), "model_used": model_used},
            llm_config_id=agent.llm.config.id
        )
        session.add(run)
        await session.commit()

        logger.success(f"✅ Optimized prompt registered as v{new_prompt.version} for {old_prompt.agent_name}")
        return {**state, "output": improved, "run_id": str(run.id)}


def agent_flow():
    workflow = StateGraph(dict)
    workflow.add_node("agent", RunnableLambda(agent_node))
    workflow.add_node("optimizer", RunnableLambda(prompt_optimizer_node))

    def router(state: Dict[str, Any]):
        if state.get("agent_name") == "prompt_optimizer":
            return "optimizer"
        return "agent"

    workflow.set_conditional_entry_point(router)
    workflow.set_finish_point("agent")
    return workflow.compile().with_config({"checkpointer": checkpointer})
