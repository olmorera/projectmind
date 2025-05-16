# projectmind/db/models/agent.py

from sqlalchemy import Column, String, Boolean, Float, Text
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
    model = Column(String, nullable=True)
    temperature = Column(Float, default=0.2)
    use_memory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
