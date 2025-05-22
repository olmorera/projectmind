from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class TaskSchema(BaseModel):
    id: UUID
    project_id: Optional[UUID]
    parent_task_id: Optional[UUID]
    agent_name: str
    task_name: Optional[str]
    description: str
    status: str
    dependencies: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
