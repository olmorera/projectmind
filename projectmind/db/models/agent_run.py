from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Text,
    JSON,
    Boolean,
    Index,
)
from sqlalchemy.sql import func
from projectmind.db.models.base import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True)

    agent_name = Column(String, nullable=False, index=True)
    task_type = Column(String, nullable=True)

    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=True)

    is_successful = Column(Boolean, nullable=True)
    effectiveness_score = Column(Float, nullable=True)

    prompt_version = Column(String, nullable=True)
    model_used = Column(String, nullable=True)
    config_used = Column(JSON, nullable=True)
    extra = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_agent_runs_agent_task", "agent_name", "task_type"),  # ✅ índice compuesto real
    )
