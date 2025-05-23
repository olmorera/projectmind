import os
import asyncio
import re
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from loguru import logger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from projectmind.workflows.agent_flow import agent_flow
from projectmind.db.models.agent import Agent

load_dotenv()

app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))

engine = create_async_engine(os.getenv("ASYNC_DATABASE_URL"), echo=False)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

def parse_message(text: str) -> tuple[str, str]:
    match = re.match(r"agent:\s*(\w+)\s*\|\s*input:\s*(.+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "planner", text.strip()

@app.message(re.compile("^(agents|help)$", re.IGNORECASE))
async def list_agents(event, say):
    async with AsyncSession() as session:
        stmt = select(Agent).where(Agent.is_active == True).order_by(Agent.name)
        result = await session.execute(stmt)
        agents = result.scalars().all()

        if not agents:
            await say("❌ No active agents found.")
            return

        message = "*🤖 Available Agents:*\n"
        for agent in agents:
            message += f"- `{agent.name}` ({agent.type}) → {agent.goal}\n"
        message += "\n_Use `agent: <name> | input: <your prompt>` to activate._"

        await say(message)

@app.message("")
async def handle_message(event, say):
    user_prompt = event.get("text", "").strip()
    user = event["user"]
    logger.info(f"📩 Message from {user}: {user_prompt}")

    if not user_prompt:
        await say("⚠️ I didn't receive any input.")
        return

    try:
        agent_name, input_text = parse_message(user_prompt)

        flow = agent_flow()

        # ✅ Aquí se corrigió con `await`
        result = await flow.ainvoke({
            "agent_name": agent_name,
            "input": input_text,
            "slack_user": user
        })

        output = result.get("output", "[No output]")
        run_id = result.get("run_id")
        extra = result.get("extra", {})
        task_count = len(extra.get("task_ids", [])) if extra else 0

        message = f"*🤖 Agent: `{agent_name}`*\n"
        message += f"*📥 Input:* `{input_text}`\n"
        message += f"*📤 Output:*\n```{output}```\n"
        if task_count:
            message += f"*📝 {task_count} tasks stored in DB.*\n"
        message += f"*🆔 Run ID:* `{run_id}`"

        await say(message)

    except Exception as e:
        logger.exception("❌ Agent error")
        await say(f"❌ Error: {str(e)}")

async def main():
    handler = AsyncSocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())
