# projectmind/workflows/agent_executor.py

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
from projectmind.utils.task_handler import try_saving_tasks
from projectmind.prompts.prompt_manager import PromptManager
from projectmind.utils.prompt_optimizer import maybe_optimize_prompt


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

        # Set prompt and format input
        agent.definition.prompt = prompt_obj.system_prompt.strip()
        if context:
            input_text = f"{context.strip()}\n\n{input_text.strip()}"

        # Run agent
        output = agent.run(input_text)

        # Save context and tasks
        await save_context(session, agent_row, agent, project, agent_name, output)
        await try_saving_tasks(session, project, agent_row, agent_name, output)

        # Register run
        run = AgentRun(
            agent_name=agent_name,
            task_type="default",
            input_data=user_input,
            output_data=output,
            is_successful=bool(output),
            effectiveness_score=None,
            prompt_version=prompt_obj.version,
            model_used=agent.llm.model.name,
            config_used={
                "temperature": agent.llm.config.temperature,
                "top_p": agent.llm.config.top_p,
                "stop_tokens": agent.llm.config.stop_tokens,
            },
            extra={
                "context_used": bool(context),
                "project_name": project.name if project else None,
                "was_translated": was_translated,
                "translated_input": translated_input if was_translated else None,
                "slack_user": slack_user
            }
        )
        session.add(run)
        await session.commit()
        logger.success(f"✅ Agent run saved: {run.id}")

        # 🧠 Evaluar y mejorar prompt si es necesario
        try:
            if agent_row.type != "evaluate":
                prompt_manager = PromptManager(session)
                await maybe_optimize_prompt(
                    agent_row,
                    prompt_manager,
                    system_prompt=prompt_obj.system_prompt.strip(),
                    user_input=user_input,
                    response=output
                )
        except Exception as e:
            logger.warning(f"⚠️ Prompt optimization failed for '{agent_name}': {e}")

        return {
            **state,
            "output": output,
            "run_id": str(run.id)
        }
