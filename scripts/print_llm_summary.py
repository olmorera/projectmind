# scripts/print_llm_summary.py
from projectmind.db.session import SessionLocal
from projectmind.db.models.llm_model import LLMModel
from projectmind.db.models.llm_config import LLMConfig
from projectmind.db.models.agent import Agent

with SessionLocal() as session:
    print("🧠 LLM MODELS:")
    for m in session.query(LLMModel).all():
        print(f"- {m.name} ({m.model})")

    print("\n⚙️ LLM CONFIGS:")
    for c in session.query(LLMConfig).all():
        print(f"- {c.name} → model_id={c.llm_model_id}")

    print("\n👤 AGENTS:")
    for a in session.query(Agent).all():
        print(f"- {a.name} → llm_config_id={a.llm_config_id}")
