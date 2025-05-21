from sqlalchemy.orm import Session
from uuid import uuid4
from projectmind.db.session import engine
from projectmind.db.models.prompt import Prompt

PROMPTS = [
    {
        "agent_name": "planner",
        "task_type": "code_generation",
        "prompt": (
            "You are a planning expert AI. Your goal is to break down the user goal into "
            "a complete, logical sequence of technical tasks. Be thorough, accurate, and include all frontend, "
            "backend, and infrastructure requirements."
        ),
        "version": 1,
    },
    {
        "agent_name": "frontend_generator",
        "task_type": "code_generation",
        "prompt": (
            "You are a frontend code generator. Based on the user input and planned tasks, generate clean, "
            "modular frontend code using the required stack (e.g. Flutter, React, Svelte). Only return code."
        ),
        "version": 1,
    },
    {
        "agent_name": "backend_generator",
        "task_type": "code_generation",
        "prompt": (
            "You are a backend infrastructure generator. Based on planned requirements, generate backend setup code "
            "for Supabase (tables, auth, RLS, buckets). Use SQL and Supabase CLI syntax."
        ),
        "version": 1,
    }
]

def seed_prompts():
    with Session(engine) as session:
        for p in PROMPTS:
            existing = session.query(Prompt).filter_by(
                agent_name=p["agent_name"],
                task_type=p["task_type"],
                version=p["version"]
            ).first()
            if not existing:
                prompt = Prompt(
                    id=uuid4(),
                    agent_name=p["agent_name"],
                    task_type=p["task_type"],
                    prompt=p["prompt"],
                    version=p["version"],
                    is_active=True
                )
                session.add(prompt)
                print(f"✅ Added prompt for {p['agent_name']} ({p['task_type']})")
        session.commit()

if __name__ == "__main__":
    seed_prompts()
