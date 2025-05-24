# scripts/bootstrap_agent_test_inputs.py

from sqlalchemy.orm import Session
from projectmind.db.session import engine
from projectmind.db.models.agent import Agent
from loguru import logger

# Define los inputs de prueba ideales por agente
DEFAULT_TEST_INPUTS = {
    "planner": "Add a calendar feature to schedule appointments.",
    "frontend_generator": "Create a login form with email and password.",
    "backend_generator": "Generate Supabase-compatible API for user profiles.",
    "code_reviewer": "Review this code: def sum(a, b): return a + b",
    "prompt_optimizer": "Improve this prompt: Write a Python function to sort a list.",
}

def bootstrap_test_inputs():
    logger.info("🧠 Initializing agent test_prompt population...")

    with Session(engine) as session:
        agents = session.query(Agent).all()
        updated = 0

        for agent in agents:
            if agent.test_prompt:
                continue

            test_prompt = DEFAULT_TEST_INPUTS.get(agent.name)
            if test_prompt:
                agent.test_prompt = test_prompt
                logger.info(f"✅ Setting test_prompt for '{agent.name}'")
                updated += 1

        session.commit()
        logger.success(f"🎯 Updated {updated} agent(s) with test_prompt.")

if __name__ == "__main__":
    bootstrap_test_inputs()
