# register_prompt.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from projectmind.prompts.prompt_manager import PromptManager
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_async_engine(os.getenv("POSTGRES_URL"))
Session = async_sessionmaker(engine, expire_on_commit=False)

async def main():
    async with Session() as session:
        manager = PromptManager(session)
        await manager.register_prompt(
            agent_type="planner",
            content="You are a planning agent. Given a user input, break it into clear tasks for software development.",
            version=1
        )

if __name__ == "__main__":
    asyncio.run(main())
