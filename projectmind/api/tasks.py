from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from projectmind.db.models.task import Task
from projectmind.db.session import async_session
from projectmind.api.schemas import TaskSchema

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{project_id}", response_model=List[TaskSchema])
async def get_tasks(project_id: UUID, session: AsyncSession = Depends(async_session)):
    result = await session.execute(
        select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks
