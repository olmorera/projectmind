# scripts/upsert_prompts.py

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from projectmind.db.session import SessionLocal
from projectmind.db.models.prompt import Prompt

prompts_data = [
    {
        "agent_name": "prompt_optimizer",
        "task_type": "default",
        "version": "1.0",
        "prompt": (
            "You are a prompt optimization expert. Improve the given failed prompt "
            "based on user feedback, without changing its original intent or style. "
            "Output only the optimized prompt text."
        ),
        "is_active": True,
    },
    {
        "agent_name": "planner",
        "task_type": "default",
        "version": "1.0",
        "prompt": (
            "You are a planning assistant. Break down the user's objective into clear, "
            "concrete, technical tasks that a developer or AI agent can execute. "
            "Avoid redundancies and keep tasks actionable."
        ),
        "is_active": True,
    },
    {
        "agent_name": "frontend_generator",
        "task_type": "default",
        "version": "1.0",
        "prompt": (
            "You are an expert frontend developer. Generate a user interface based on the user's input, "
            "using Svelte framework with Tailwind CSS for styling. "
            "Output only the UI code files required, keep it minimal and clean."
        ),
        "is_active": True,
    },
    {
        "agent_name": "backend_generator",
        "task_type": "default",
        "version": "1.0",
        "prompt": (
            "You are an expert backend developer. Based on the user's input, generate backend logic "
            "for Supabase including PostgreSQL schema, RLS policies, Edge Functions if needed, and APIs. "
            "Output only the necessary code snippets and configurations."
        ),
        "is_active": True,
    },
]

def upsert_prompts():
    session = SessionLocal()
    try:
        for data in prompts_data:
            stmt = select(Prompt).where(
                Prompt.agent_name == data["agent_name"],
                Prompt.task_type == data["task_type"]
            )
            result = session.execute(stmt).scalars().first()
            if result:
                # Update existing
                result.version = data["version"]
                result.prompt = data["system_prompt"]
                result.is_active = data["is_active"]
            else:
                # Insert new
                prompt = Prompt(**data)
                session.add(prompt)
        session.commit()
        print("Prompts upsert completed successfully.")
    except Exception as e:
        session.rollback()
        print("Error upserting prompts:", e)
    finally:
        session.close()

if __name__ == "__main__":
    upsert_prompts()
