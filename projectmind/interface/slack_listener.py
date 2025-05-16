# projectmind/interface/slack_listener.py

import os
import asyncio
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from projectmind.workflows.planner_flow import planner_flow
from loguru import logger

load_dotenv()

app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))

@app.message("")
async def handle_message(event, say):
    user_input = event.get("text", "").strip()
    user = event["user"]
    logger.info(f"📩 Received message from {user}: {user_input}")

    if not user_input:
        await say("⚠️ I didn't receive any input.")
        return

    try:
        flow = planner_flow()
        result = await flow.ainvoke({"input": user_input})
        output = result.get("planner_output", "[No output]")
        task_ids = result.get("task_ids", [])

        message = f"*🧠 Planner Output:*\n```{output}```\n"
        message += f"*📝 {len(task_ids)} tasks generated and stored in DB.*"
        await say(message)

    except Exception as e:
        logger.exception("❌ Error handling message")
        await say(f"❌ Error: {str(e)}")

async def main():
    handler = AsyncSocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())
