# scripts/run_agent.py

import argparse
import asyncio
from loguru import logger
from projectmind.workflows.flow_builder import agent_flow  # <- actualizamos esto


async def main():
    parser = argparse.ArgumentParser(description="Run a ProjectMind agent with input and optional project context")
    parser.add_argument("agent", help="Agent name (e.g., planner, frontend_generator)")
    parser.add_argument("input", help="User input for the agent")
    parser.add_argument("--project_name", help="Project name to scope memory/context", required=False)
    parser.add_argument("--user_id", help="Slack user ID (optional)", required=False)

    args = parser.parse_args()

    logger.info(f"🔁 Running agent: {args.agent}")
    logger.info(f"📝 Input: {args.input}")

    flow = agent_flow()
    result = await flow.ainvoke({
        "agent_name": args.agent,
        "input": args.input,
        "project_name": args.project_name,
        "slack_user": args.user_id
    })

    logger.success("✅ Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
