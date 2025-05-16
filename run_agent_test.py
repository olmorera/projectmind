import asyncio
from projectmind.workflows.agent_flow import agent_flow

async def main():
    flow = agent_flow()

    result = await flow.ainvoke({
        "agent_name": "planner",
        "input": "Build an app to manage book rentals",
        "slack_user": "U08RMCF50DU"
    })

    print("\n📦 Final result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
