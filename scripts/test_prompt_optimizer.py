# scripts/test_prompt_optimizer.py

import asyncio
from loguru import logger
from projectmind.workflows.agent_flow import agent_flow

# 🧪 Reemplaza con un ID real de tu tabla "prompts"
PROMPT_ID = "REPLACE_WITH_REAL_PROMPT_ID"

async def main():
    flow = agent_flow()

    state = {
        "agent_name": "prompt_optimizer",
        "input": {
            "prompt_id": PROMPT_ID,
            "success": False,
            "feedback": "The prompt is too vague and lacks clear structure."
        },
        "slack_user": "test_user"
    }

    logger.info("🚀 Starting prompt_optimizer test...")
    result = await flow.ainvoke(state)
    logger.success("🎯 Optimizer finished:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
