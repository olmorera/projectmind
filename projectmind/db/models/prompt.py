# projectmind/db/models/prompt.py

from sqlalchemy import Column, String, Boolean, Float, DateTime, func, Index, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from projectmind.db.models.base import Base

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String, nullable=False, index=True)
    task_type = Column(String, default="default", index=True)
    version = Column(String, default="1.0")
    system_prompt = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    effectiveness_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index("ix_prompts_agent_task", "agent_name", "task_type", "is_active"),
    )
