# projectmind/db/models/task.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from projectmind.db.models.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)  # <-- ForeignKey agregado aquí
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    agent_name = Column(String(50), nullable=False, index=True)
    task_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)
    dependencies = Column(Text, nullable=True)

    __table_args__ = (
        Index('ix_project_status', 'project_id', 'status'),
    )
