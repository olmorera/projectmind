# projectmind/db/models/llm_model.py

from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .base import Base

class LLMModel(Base):
    __tablename__ = "llm_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    provider = Column(String, nullable=False)           # llama / openai / ...
    model = Column(String, nullable=False)              # ruta GGUF o nombre OpenAI

    # Recursos
    n_threads = Column(Integer, default=8)
    n_batch = Column(Integer, default=64)

    # 🔧 Configuraciones técnicas extendidas para llama.cpp
    chat_format = Column(String, nullable=True)             # "llama-2", "chatml", etc.
    n_ctx = Column(Integer, default=4096)                   # Context window size
    numa = Column(Integer, default=1)                       # NUMA-aware execution
    mixture_of_experts = Column(Boolean, default=False)
    rope_scaling_type = Column(Integer, nullable=True)      # 2 para WizardCoder, etc.
    f16_kv = Column(Boolean, default=False)                 # KV cache en FP16
    use_mlock = Column(Boolean, default=False)              # Evitar swap
    use_mmap = Column(Boolean, default=True)                # Usar mmap en carga
    low_vram = Column(Boolean, default=False)
    offload_kqv = Column(Boolean, default=False)
    embedding = Column(Boolean, default=False)
    logits_all = Column(Boolean, default=False)
    verbose = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
