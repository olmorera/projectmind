# scripts/get_last_planner_runs.py

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, desc
from dotenv import load_dotenv
from datetime import datetime
import os

from projectmind.db.models.planner_run import PlannerRun

load_dotenv()

engine = create_async_engine(os.getenv("POSTGRES_URL"), echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def main(limit: int = 5):
    async with Session() as session:
        stmt = (
            select(PlannerRun)
            .order_by(desc(PlannerRun.created_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        runs = result.scalars().all()

        if not runs:
            print("❌ No planner runs found.")
            return

        for run in runs:
            print("─" * 60)
            print(f"🆔 Run ID:     {run.id}")
            print(f"👤 User ID:    {run.user_id or 'N/A'}")
            print(f"📅 Timestamp:  {run.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📥 Prompt:\n{run.input_prompt}")
            print(f"📤 Response:\n{run.output_response}")
            print(f"📝 Task IDs:   {', '.join(run.task_ids or [])}")
        print("─" * 60)

if __name__ == "__main__":
    asyncio.run(main())
