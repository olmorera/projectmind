# projectmind/db/models/agent.py

from sqlalchemy import Column, String, Boolean, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
import uuid
from projectmind.db.models.base import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)       # planner, generator, etc.
    goal = Column(Text, nullable=False)
    llm_config_id = Column(UUID(as_uuid=True), ForeignKey("llm_configs.id"), nullable=True)
    use_memory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
