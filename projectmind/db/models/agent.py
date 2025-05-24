from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
import uuid
from projectmind.db.models.base import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    goal = Column(Text, nullable=False)
    test_prompt = Column(Text, nullable=True)
    llm_config_id = Column(UUID(as_uuid=True), ForeignKey("llm_configs.id"), nullable=True)
    use_memory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    optimize_prompt = Column(Boolean, default=True)
    can_create_tasks = Column(Boolean, default=False, index=True)
    can_read_tasks = Column(Boolean, default=False, index=True)
    can_execute_tasks = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index('ix_agents_type_active', 'type', 'is_active'),
    )
