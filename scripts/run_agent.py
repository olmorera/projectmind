# scripts/run_agent.py

import argparse
import asyncio
from loguru import logger
from projectmind.workflows.agent_flow import agent_flow


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", help="Agent name (e.g., planner, frontend_generator)")
    parser.add_argument("input", help="User input for the agent")
    parser.add_argument("--project_id", help="Project ID to scope memory/context", required=False)
    parser.add_argument("--user_id", help="Slack user ID (optional)", required=False)

    args = parser.parse_args()

    logger.info(f"🔁 Running agent: {args.agent}")
    logger.info(f"📝 Input: {args.input}")

    flow = agent_flow()
    result = await flow.ainvoke({
        "agent_name": args.agent,
        "input": args.input,
        "project_id": args.project_id,
        "slack_user": args.user_id
    })

    logger.success("✅ Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
