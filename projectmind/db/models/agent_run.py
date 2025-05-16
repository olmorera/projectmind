# projectmind/db/models/agent_run.py

from sqlalchemy import Column, String, DateTime, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from projectmind.db.models.base import Base

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index("ix_agent_runs_agent_created", "agent_name", "created_at"),
    )
