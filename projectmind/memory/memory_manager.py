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

    async def set(self, key: str, value: str, session: AsyncSession):
        if value and len(value.strip()) > 20:
            try:
                stmt = insert(Memory).values(
                    namespace=self.namespace,
                    key=key,
                    value=value
                )
                await session.execute(stmt)
                await session.commit()
                logger.success(f"🧠 Memory stored under key: {key}")
            except Exception as e:
                logger.error(f"❌ Memory set error: {e}")
        else:
            logger.info("📭 Output not valuable enough to store.")
