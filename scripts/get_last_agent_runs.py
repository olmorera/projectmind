import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, desc
from projectmind.db.models.agent_run import AgentRun

load_dotenv()

engine = create_async_engine(os.getenv("POSTGRES_URL"), echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def main(agent_name: str = None, limit: int = 5):
    async with Session() as session:
        stmt = select(AgentRun).order_by(desc(AgentRun.created_at)).limit(limit)

        if agent_name:
            stmt = stmt.where(AgentRun.agent_name == agent_name)

        result = await session.execute(stmt)
        runs = result.scalars().all()

        if not runs:
            print("❌ No agent runs found.")
            return

        for run in runs:
            print("─" * 60)
            print(f"🧠 Agent:       {run.agent_name}")
            print(f"🆔 Run ID:      {run.id}")
            print(f"👤 User ID:     {run.user_id or 'N/A'}")
            print(f"📅 Timestamp:   {run.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📥 Input:\n{run.input}")
            print(f"📤 Output:\n{run.output}")
            if run.extra:
                print(f"🗂️ Extra:       {run.extra}")
        print("─" * 60)

if __name__ == "__main__":
    import sys
    agent = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(agent_name=agent))
