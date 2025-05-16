# scripts/run_agent.py
import sys
import asyncio
from loguru import logger
from projectmind.workflows.agent_flow import agent_flow

async def main():
    if len(sys.argv) < 3:
        print("Usage: run_agent.py <agent_name> <input_text>")
        sys.exit(1)

    agent_name = sys.argv[1]
    input_text = sys.argv[2]

    logger.info(f"🔁 Running agent: {agent_name}")
    logger.info(f"📝 Input: {input_text}")

    flow = agent_flow()
    result = await flow.ainvoke({
        "agent_name": agent_name,
        "input": input_text
    })

    print("\n✅ Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
