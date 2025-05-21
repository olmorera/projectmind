# projectmind/db/models/memory.py

from sqlalchemy import Column, String, DateTime, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace = Column(String, nullable=False)
    key = Column(String, nullable=True)
    value = Column(Text, nullable=False)
    project_id = Column(String, nullable=True)
    agent_name = Column(String, nullable=True)
    task_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_memory_namespace_key", "namespace", "key"),
        Index("ix_memory_created_at", "created_at"),
        Index("ix_memory_project_agent_task", "project_id", "agent_name", "task_type"),
    )
