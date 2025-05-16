# scripts/run_agent.py

import asyncio
import sys
from projectmind.workflows.agent_flow import agent_flow


async def main():
    if len(sys.argv) < 3:
        print("Usage: poetry run python scripts/run_agent.py <agent_name> <task_input>")
        return

    agent_name = sys.argv[1]
    task_input = " ".join(sys.argv[2:])

    print(f"🔁 Running agent: {agent_name}")
    print(f"📝 Input: {task_input}\n")

    # Ejecutar flujo compilado
    flow = agent_flow()
    result = await flow.invoke({
        "agent_name": agent_name,
        "input": task_input
    })

    print("\n✅ Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
