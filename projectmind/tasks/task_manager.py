import re
import string
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from projectmind.db.models.task import Task
from loguru import logger

def normalize_task_name(name: str) -> str:
    name = name.strip().lower()
    return name.translate(str.maketrans('', '', string.punctuation))

async def save_tasks_from_output(
    project_id: UUID,
    agent_name: str,
    output_text: str,
    session: AsyncSession
):
    tasks = re.findall(r'^-\s(.+)', output_text, re.MULTILINE)
    saved = 0

    try:
        for task_desc in tasks:
            task_name = normalize_task_name(task_desc[:100])

            exists_query = select(Task).where(
                Task.project_id == project_id,
                Task.agent_name == agent_name,
                Task.task_name == task_name,
            )
            exists = await session.scalar(exists_query)

            if exists:
                logger.debug(f"Task already exists, skipping: {task_name}")
                continue

            task = Task(
                project_id=project_id,
                agent_name=agent_name,
                task_name=task_name,
                description=task_desc,
                status="pending"
            )
            session.add(task)
            saved += 1
        await session.commit()
        logger.success(f"Saved {saved} new tasks for project {project_id} by agent {agent_name}")

    except Exception as e:
        await session.rollback()
        logger.error(f"Error saving tasks: {e}")
        raise
