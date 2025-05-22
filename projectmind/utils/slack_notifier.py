# projectmind/utils/slack_notifier.py

import os
import httpx
from loguru import logger

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

async def notify_slack(data: dict):
    if not SLACK_WEBHOOK_URL:
        logger.warning("⚠️ SLACK_WEBHOOK_URL not set. Skipping Slack notification.")
        return

    try:
        agent = data.get("agent")
        model_used = data.get("model_used")
        version_old = data.get("version_old")
        version_new = data.get("version_new")
        score_old = data.get("score_old", "N/A")
        score_new = data.get("score_new", "N/A")

        original = data.get("original", "").strip()
        improved = data.get("improved", "").strip()

        message = f"""
🧠 *Prompt optimized for agent:* `{agent}`
🧪 *Model used:* `{model_used}`
📈 *Score improved:* `{score_old}` ➜ `{score_new}`
📄 *Version:* `v{version_old}` ➜ `v{version_new}`

*📝 Original prompt:*
```text
{original}
```

*✅ Improved prompt:*
```text
{improved}
```
"""

        async with httpx.AsyncClient() as client:
            await client.post(SLACK_WEBHOOK_URL, json={"text": message})
        logger.success(f"📤 Slack notification sent for agent '{agent}'")

    except Exception as e:
        logger.error(f"❌ Failed to send Slack notification: {e}")