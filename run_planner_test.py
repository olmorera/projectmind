# run_planner_test.py

import asyncio
from projectmind.workflows.planner_flow import planner_flow

async def main():
    state = {"input": "Build an app to manage book rentals"}
    flow = planner_flow()
    result = await flow.ainvoke(state)
    print("\n📦 Result:\n", result["planner_output"])

if __name__ == "__main__":
    asyncio.run(main())
