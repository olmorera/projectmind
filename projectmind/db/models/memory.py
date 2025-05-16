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
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Índices para búsquedas eficientes
    __table_args__ = (
        Index("ix_memory_namespace_key", "namespace", "key"),
        Index("ix_memory_created_at", "created_at"),
    )
