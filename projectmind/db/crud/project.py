# projectmind/db/crud/project.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from projectmind.db.models.project import Project
import logging

logger = logging.getLogger(__name__)

async def get_project_by_id(session: AsyncSession, project_id: UUID) -> Project | None:
    result = await session.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()

async def get_project_by_name(session: AsyncSession, name: str) -> Project | None:
    result = await session.execute(select(Project).where(Project.name == name))
    return result.scalar_one_or_none()

async def create_project(session: AsyncSession, project_id: str, name: str = None, description: str = "") -> Project:
    project = Project(
        id=project_id,
        name=name or f"Project {project_id}",
        description=description,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    logger.info(f"Created new project with id {project_id}")
    return project
