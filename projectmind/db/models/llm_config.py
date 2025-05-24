# projectmind/db/models/llm_config.py

from sqlalchemy import Column, String, Float, Integer, DateTime,  ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class LLMConfig(Base):
    __tablename__ = "llm_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    llm_model_id = Column(UUID(as_uuid=True), ForeignKey("llm_models.id"), nullable=False)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1024)
    top_p = Column(Float, default=1.0)
    stop_tokens = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
