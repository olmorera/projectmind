# scripts/switch_planner_model.py

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv
import os

from projectmind.db.models import LLMModel, LLMConfig, Agent

load_dotenv()
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

MODEL_FILENAME = "zephyr-7b-beta.Q5_K_M.gguf"
MODEL_NAME = "zephyr-7b-beta.q5-k-m"
MODEL_PATH = f"/home/olmorera/AI/models/{MODEL_FILENAME}"

async def switch_planner_model():
    async with AsyncSessionLocal() as session:
        # ✅ Buscar modelo
        result = await session.execute(select(LLMModel).where(LLMModel.name == MODEL_NAME))
        model = result.scalar_one_or_none()

        if not model:
            model = LLMModel(
                id=uuid.uuid4(),
                name=MODEL_NAME,
                provider="llama",
                model=MODEL_PATH,
                n_threads=48,
                n_batch=64,
                chat_format="chatml",
                n_ctx=8192,
                rope_scaling_type=None,
                f16_kv=False,
                use_mlock=False,
                use_mmap=True,
                low_vram=False,
                offload_kqv=False,
                embedding=False,
                logits_all=False,
                verbose=True,
                numa=1
            )
            session.add(model)
            await session.flush()
            print(f"✅ Registered model: {MODEL_NAME}")

        # ✅ Crear config si no existe
        config_name = f"{MODEL_NAME}-planner"
        result = await session.execute(select(LLMConfig).where(LLMConfig.name == config_name))
        config = result.scalar_one_or_none()

        if not config:
            config = LLMConfig(
                id=uuid.uuid4(),
                name=config_name,
                llm_model_id=model.id,
                temperature=0.7,
                max_tokens=1024,
                top_p=1.0,
                stop_tokens="</s>,```"
            )
            session.add(config)
            await session.flush()
            print(f"✅ Created config: {config_name}")

        # ✅ Actualizar agente
        result = await session.execute(select(Agent).where(Agent.name == "planner"))
        planner = result.scalar_one_or_none()
        if not planner:
            print("❌ Agent 'planner' not found.")
            return

        planner.llm_config_id = config.id
        await session.commit()
        print(f"🚀 Agent 'planner' updated to use '{MODEL_NAME}'")

if __name__ == "__main__":
    asyncio.run(switch_planner_model())
