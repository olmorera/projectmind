# scripts/register_mixtral_for_planner.py

import asyncio
import uuid
from datetime import datetime

from projectmind.db.session_async import get_async_session
from projectmind.db.models.llm_model import LLMModel
from projectmind.db.models.llm_config import LLMConfig
from projectmind.db.models.agent import Agent

async def main():
    async for session in get_async_session():
        # 1. Create model
        llm_model = LLMModel(
            id=uuid.uuid4(),
            name="mixtral-8x7b-instruct-q5_k_m",
            provider="llama",
            model="mixtral-8x7b-instruct-v0.1.Q5_K_M.gguf",
            n_threads=28,
            n_batch=32,
            chat_format="chatml",
            n_ctx=32768,
            numa=1,
            rope_scaling_type=2,
            f16_kv=False,
            use_mlock=False,
            use_mmap=True,
            low_vram=False,
            offload_kqv=False,
            embedding=False,
            logits_all=False,
            verbose=True
        )
        session.add(llm_model)
        await session.flush()

        # 2. Create config
        llm_config = LLMConfig(
            id=uuid.uuid4(),
            name="mixtral-for-planner",
            llm_model_id=llm_model.id,
            temperature=0.3,
            max_tokens=2048,
            top_p=0.95,
            stop_tokens=None
        )
        session.add(llm_config)
        await session.flush()

        # 3. Assign to planner (❌ sin updated_at si no está en el modelo)
        await session.execute(
            Agent.__table__.update()
            .where(Agent.name == "planner")
            .values(llm_config_id=llm_config.id)
        )

        await session.commit()
        print("✅ Mixtral registered and assigned to planner.")

if __name__ == "__main__":
    asyncio.run(main())
