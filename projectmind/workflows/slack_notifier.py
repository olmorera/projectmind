# projectmind/workflows/slack_notifier.py

import os
from slack_sdk.web.async_client import AsyncWebClient
from loguru import logger

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#projectmind")

if not SLACK_BOT_TOKEN:
    raise RuntimeError("❌ SLACK_BOT_TOKEN is not set in .env")

client = AsyncWebClient(token=SLACK_BOT_TOKEN)


async def notify_slack(data: dict):
    try:
        text = (
            f"🔧 *Prompt optimized for `{data['agent']}`*\n"
            f"> *Old (v{data['version_old']}):*\n```{data['original']}```\n"
            f"> *New (v{data['version_new']}):*\n```{data['improved']}```\n"
            f"> 🧠 *Model used:* `{data['model_used']}`"
        )
        await client.chat_postMessage(channel=SLACK_CHANNEL, text=text)
        logger.info(f"📣 Slack notified of prompt optimization for {data['agent']}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to send Slack notification: {e}")
