# projectmind/memory/memory_manager.py

from loguru import logger
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from projectmind.db.models.memory import Memory


class MemoryManager:
    def __init__(self, namespace: str = "task_outputs"):
        self.namespace = namespace

    async def get(self, keys: list[str], session: AsyncSession) -> str | None:
        try:
            stmt = (
                select(Memory)
                .where(Memory.namespace == self.namespace)
                .where(Memory.key.in_(keys))
                .order_by(Memory.created_at.desc())
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            values = [r.value for r in rows if r.value]
            return "\n".join(values) if values else None
        except Exception as e:
            logger.error(f"❌ Memory get error: {e}")
            return None

    async def get_project_context(
        self,
        project_id: str,
        agent_name: str,
        task_type: str,
        session: AsyncSession
    ) -> list[str]:
        try:
            stmt = (
                select(Memory)
                .where(Memory.namespace == self.namespace)
                .where(Memory.project_id == project_id)
                .where(Memory.agent_name == agent_name)
                .where(Memory.task_type == task_type)
                .order_by(Memory.created_at.desc())
                .limit(10)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [r.value for r in rows if r.value]
        except Exception as e:
            logger.error(f"❌ Memory get_project_context error: {e}")
            return []

    async def save_project_context(
        self,
        project_id: str,
        agent_name: str,
        task_type: str,
        content: str,
        session: AsyncSession
    ):
        if content and len(content.strip()) > 20:
            try:
                stmt = insert(Memory).values(
                    namespace=self.namespace,
                    project_id=project_id,
                    agent_name=agent_name,
                    task_type=task_type,
                    key=f"{agent_name}:{task_type}:last",
                    value=content
                )
                await session.execute(stmt)
                await session.commit()
                logger.success(
                    f"🧠 Project memory stored for {agent_name}:{task_type} in project {project_id}"
                )
            except Exception as e:
                logger.error(f"❌ Memory save_project_context error: {e}")
        else:
            logger.info("📭 Output not valuable enough to store.")
