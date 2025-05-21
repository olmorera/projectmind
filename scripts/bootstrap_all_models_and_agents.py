# scripts/bootstrap_all_models_and_agents.py

import asyncio
import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from projectmind.db.models import LLMModel, LLMConfig, Agent, Prompt

load_dotenv()
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 📂 Ruta de modelos
MODELS_DIR = "/home/olmorera/AI/models/"

# 🤖 Agentes con modelo recomendado
AGENT_DEFINITIONS = {
    "prompt_optimizer": {
        "type": "optimize",
        "goal": "Improve failed prompts for clarity and effectiveness.",
        "model_file": "wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
        "prompt": """You are a prompt optimization expert. Improve the following failed prompt based on user feedback, without changing its original intent. Make it clearer, more specific, and effective.

Prompt: {{failed_prompt}}

Feedback: {{feedback}}"""
    },
    "planner": {
        "type": "plan",
        "goal": "Break down the user's objective into clear, technical tasks that a developer or AI agent can execute.",
        "model_file": "phi-2.Q4_K_M.gguf",
        "prompt": """You are a planning assistant. Break down the user's objective into clear, technical tasks that a developer or AI agent can execute, including dependencies when relevant."""
    },
    "frontend_generator": {
        "type": "frontend",
        "goal": "Generate frontend UIs using frameworks like Flutter, React or Svelte.",
        "model_file": "Nous-Hermes-2-Mistral-7B-DPO.Q5_K_M.gguf",
        "prompt": """You are an expert frontend developer. Generate a user interface based on the user's input, using the requested framework (e.g., Flutter, Svelte, React). Ensure clean structure, good UX, and accessibility."""
    },
    "backend_generator": {
        "type": "backend",
        "goal": "Generate backend logic and Supabase-based services.",
        "model_file": "codellama-34b-instruct.Q4_K_M.gguf",
        "prompt": """You are an expert backend developer. Based on the user’s input, generate the logic for a backend API or service using Supabase or the specified backend technology. Ensure database access is secure and optimized."""
    }
}

# 🛠️ Configuración recomendada por modelo base
MODEL_CONFIGS = {
    "wizardcoder-python-34b-v1.0.Q5_K_M.gguf": dict(chat_format="llama-2", n_ctx=16384, rope_scaling_type=2),
    "phi-2.Q4_K_M.gguf": dict(chat_format="llama-2", n_ctx=4096),
    "Nous-Hermes-2-Mistral-7B-DPO.Q5_K_M.gguf": dict(chat_format="chatml", n_ctx=8192),
    "codellama-34b-instruct.Q4_K_M.gguf": dict(chat_format="llama-2", n_ctx=8192)
}

def build_model_name(filename: str) -> str:
    return filename.replace(".gguf", "").replace("_", "-").lower()

async def bootstrap():
    async with AsyncSessionLocal() as session:
        print("🚀 Starting agent + model + prompt bootstrap...\n")

        for agent_name, agent_def in AGENT_DEFINITIONS.items():
            model_file = agent_def["model_file"]
            model_path = os.path.join(MODELS_DIR, model_file)

            if not os.path.exists(model_path):
                print(f"⚠️ Model file not found: {model_path}")
                continue

            model_name = build_model_name(model_file)

            # 🔁 Reutilizar si ya existe
            result = await session.execute(LLMModel.__table__.select().where(LLMModel.name == model_name))
            model_row = result.scalar_one_or_none()

            if not model_row:
                model_row = LLMModel(
                    id=uuid.uuid4(),
                    name=model_name,
                    provider="llama",
                    model=model_path,
                    n_threads=48,
                    n_batch=64,
                    chat_format=MODEL_CONFIGS[model_file].get("chat_format", "llama-2"),
                    n_ctx=MODEL_CONFIGS[model_file].get("n_ctx", 4096),
                    rope_scaling_type=MODEL_CONFIGS[model_file].get("rope_scaling_type", None),
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
                session.add(model_row)
                await session.flush()
                print(f"✅ Registered model: {model_name}")

            # 📦 Configuración
            config_name = f"{model_name}-default"
            config = LLMConfig(
                id=uuid.uuid4(),
                name=config_name,
                llm_model_id=model_row.id,
                temperature=0.7,
                max_tokens=1024,
                top_p=1.0,
                stop_tokens="</s>,```"
            )
            session.add(config)
            await session.flush()

            # 🤖 Agente
            agent = Agent(
                id=uuid.uuid4(),
                name=agent_name,
                type=agent_def["type"],
                goal=agent_def["goal"],
                llm_config_id=config.id,
                use_memory=False,
                is_active=True
            )
            session.add(agent)
            await session.flush()
            print(f"🤖 Agent '{agent_name}' created using model '{model_name}'")

            # 🧠 Prompt inicial optimizado
            prompt = Prompt(
                id=uuid.uuid4(),
                agent_name=agent_name,
                task_type="default",
                version="1.0",
                prompt=agent_def["prompt"],
                is_active=True,
                effectiveness_score=0.0
            )
            session.add(prompt)

        await session.commit()
        print("\n✅ Bootstrap completed with optimized prompts.")

if __name__ == "__main__":
    asyncio.run(bootstrap())
