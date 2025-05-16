# scripts/reset_llm_models.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import uuid4
from projectmind.db.session import engine
from projectmind.db.models.llm_model import LLMModel
from projectmind.db.models.llm_config import LLMConfig
from projectmind.db.models.agent import Agent

def reset_llm_models():
    with Session(engine) as session:
        # Limpiar referencias previas y datos bloqueantes
        print("🧹 Cleaning agent_runs, agents.llm_config_id, llm_configs and llm_models...")

        # 1. Borrar ejecuciones de agentes
        session.execute(text("DELETE FROM agent_runs"))

        # 2. Desvincular llm_config_id de agentes
        session.query(Agent).update({Agent.llm_config_id: None})

        # 3. Borrar configuraciones y modelos antiguos
        session.query(LLMConfig).delete()
        session.query(LLMModel).delete()
        session.commit()

        print("✅ Inserting optimized LLM models...")

        # Crear modelos optimizados
        models = {
            "wizardcoder": LLMModel(
                id=uuid4(),
                name="wizardcoder-python-34b-v1.0",
                provider="llama",
                model="/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
                n_threads=48,
                n_batch=64,
                chat_format="llama-2",
                n_ctx=16384,
                numa=1,
                rope_scaling_type=2,
                f16_kv=False,
                use_mlock=False,
                use_mmap=True,
                low_vram=False,
                offload_kqv=False,
                embedding=False,
                logits_all=False,
                verbose=False,
            ),
            "mixtral": LLMModel(
                id=uuid4(),
                name="mixtral-8x7b-instruct",
                provider="llama",
                model="/home/olmorera/AI/models/mixtral-8x7b-instruct.Q5_K_M.gguf",
                n_threads=48,
                n_batch=32,
                chat_format="chatml",
                n_ctx=8192,
                numa=1,
                rope_scaling_type=1,
                f16_kv=False,
                use_mlock=False,
                use_mmap=True,
                low_vram=True,
                offload_kqv=True,
                embedding=False,
                logits_all=False,
                verbose=False,
            ),
            "zephyr": LLMModel(
                id=uuid4(),
                name="zephyr-7b-beta",
                provider="llama",
                model="/home/olmorera/AI/models/zephyr-7b-beta.Q5_K_M.gguf",
                n_threads=48,
                n_batch=48,
                chat_format="chatml",
                n_ctx=8192,
                numa=1,
                rope_scaling_type=1,
                f16_kv=False,
                use_mlock=False,
                use_mmap=True,
                low_vram=True,
                offload_kqv=True,
                embedding=False,
                logits_all=False,
                verbose=False,
            ),
            "openchat": LLMModel(
                id=uuid4(),
                name="openchat-3.5",
                provider="llama",
                model="/home/olmorera/AI/models/openchat-3.5.Q5_K_M.gguf",
                n_threads=48,
                n_batch=48,
                chat_format="chatml",
                n_ctx=8192,
                numa=1,
                rope_scaling_type=1,
                f16_kv=False,
                use_mlock=False,
                use_mmap=True,
                low_vram=True,
                offload_kqv=True,
                embedding=False,
                logits_all=False,
                verbose=False,
            ),
        }

        session.add_all(models.values())
        session.commit()

        print("✅ Inserting LLM configs...")

        configs = {
            "wizardcoder_config": LLMConfig(
                id=uuid4(),
                name="wizardcoder-default",
                llm_model_id=models["wizardcoder"].id,
                temperature=0.2,
                top_p=0.9,
                max_tokens=2048,
            ),
            "mixtral_config": LLMConfig(
                id=uuid4(),
                name="mixtral-default",
                llm_model_id=models["mixtral"].id,
                temperature=0.4,
                top_p=0.95,
                max_tokens=2048,
            ),
            "zephyr_config": LLMConfig(
                id=uuid4(),
                name="zephyr-default",
                llm_model_id=models["zephyr"].id,
                temperature=0.6,
                top_p=0.95,
                max_tokens=2048,
            ),
            "openchat_config": LLMConfig(
                id=uuid4(),
                name="openchat-default",
                llm_model_id=models["openchat"].id,
                temperature=0.7,
                top_p=1.0,
                max_tokens=2048,
            ),
        }

        session.add_all(configs.values())
        session.commit()

        print("✅ Assigning LLM configs to agents...")

        agent_map = {
            "planner": configs["mixtral_config"].id,
            "frontend_generator": configs["wizardcoder_config"].id,
            "backend_generator": configs["wizardcoder_config"].id,
        }

        agents = session.query(Agent).filter(Agent.name.in_(agent_map.keys())).all()
        for agent in agents:
            agent.llm_config_id = agent_map[agent.name]

        session.commit()
        print("🎉 Done. ProjectMind LLM setup is now clean and optimized.")

if __name__ == "__main__":
    reset_llm_models()
