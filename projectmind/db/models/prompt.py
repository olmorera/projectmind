# projectmind/db/models/prompt.py
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from projectmind.db.models.base import Base

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(String, nullable=False)  # e.g., planner, frontend_generator
    version = Column(Integer, default=1)
    content = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    effectiveness_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
