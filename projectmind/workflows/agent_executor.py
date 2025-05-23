import uuid
from typing import Dict, Any
from sqlalchemy import select
from loguru import logger

from projectmind.agents.agent_factory import AgentFactory
from projectmind.db.models import AgentRun, Prompt, Agent
from projectmind.utils.language_utils import translate_to_english
from projectmind.utils.slack_notifier import notify_slack
from projectmind.db.crud.project import get_project_by_name, create_project

from projectmind.db.session_async import AsyncSessionLocal
from projectmind.utils.context_handler import load_context, save_context
from projectmind.utils.prompt_optimizer import maybe_optimize_prompt
from projectmind.utils.task_handler import try_saving_tasks
from projectmind.llm.prompt_formatter import format_prompt


async def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_name = state.get("agent_name")
    user_input = state.get("input")
    project_name = state.get("project_name")
    slack_user = state.get("slack_user")

    if not agent_name or user_input is None:
        raise ValueError("Missing 'agent_name' and/or 'input' in state")

    logger.info(f"🤖 Executing agent: {agent_name}")

    async with AsyncSessionLocal() as session:
        # Get or create project
        project = None
        if project_name:
            project = await get_project_by_name(session, project_name)
            if not project:
                project = await create_project(session, str(uuid.uuid4()), name=project_name)

        # Load agent
        agent = AgentFactory.create(agent_name)

        # Translate if needed
        translated_input, was_translated = translate_to_english(user_input)
        input_text = translated_input if was_translated else user_input

        if was_translated:
            await notify_slack({
                "agent": agent_name,
                "note": "Input was auto-translated to English.",
                "original_input": user_input,
                "translated_input": translated_input
            })

        # Get prompt
        prompt_obj = (
            await session.execute(
                select(Prompt)
                .where(Prompt.agent_name == agent_name, Prompt.task_type == "default", Prompt.is_active == True)
                .order_by(Prompt.version.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

        if not prompt_obj:
            raise ValueError(f"No active prompt found for agent '{agent_name}'")

        # Get agent config row
        agent_row = (
            await session.execute(select(Agent).where(Agent.name == agent_name))
        ).scalar_one()

        # Load context
        context = await load_context(session, agent_row, agent, project, agent_name)

        # ✅ Asignar prompt al agente y construir input final con contexto
        agent.definition.prompt = prompt_obj.prompt.strip()

        if context:
            input_text = f"{context.strip()}\n\n{input_text.strip()}"

        # ✅ Ejecutar usando lógica centralizada en BaseAgent
        output = agent.run(input_text)

        # Save context and tasks
        await save_context(session, agent_row, agent, project, agent_name, output)
        await try_saving_tasks(session, project, agent_row, agent_name, output)

        # Register run
        run = AgentRun(
            id=uuid.uuid4(),
            agent_name=agent_name,
            user_id=slack_user,
            input=user_input,
            output=output,
            extra={
                "context_used": bool(context),
                "project_name": project.name if project else None,
                "was_translated": was_translated,
                "translated_input": translated_input if was_translated else None
            },
            llm_config_id=agent.llm.config.id
        )
        session.add(run)
        await session.commit()
        logger.success(f"✅ Agent run saved: {run.id}")

        # Optimize prompt if needed
        await maybe_optimize_prompt(session, agent_row, agent, prompt_obj, output)

        return {
            **state,
            "output": output,
            "run_id": str(run.id)
        }
