from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from projectmind.db.models.base import Base

class PlannerRun(Base):
    __tablename__ = "planner_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=True)  # Slack user ID o similar
    input_prompt = Column(Text, nullable=False)
    output_response = Column(Text, nullable=False)
    task_ids = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
