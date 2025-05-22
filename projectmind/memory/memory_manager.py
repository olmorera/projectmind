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
        project_id: str | None = None,
        project_name: str | None = None,
        agent_name: str = "",
        task_type: str = "",
        session: AsyncSession = None
    ) -> list[str]:
        try:
            stmt = select(Memory).where(Memory.namespace == self.namespace)

            if project_id:
                stmt = stmt.where(Memory.project_id == project_id)
            elif project_name:
                stmt = stmt.where(Memory.project_name == project_name)
            else:
                logger.warning("⚠️ No project_id or project_name provided for memory retrieval.")
                return []

            if agent_name:
                stmt = stmt.where(Memory.agent_name == agent_name)
            if task_type:
                stmt = stmt.where(Memory.task_type == task_type)

            stmt = stmt.order_by(Memory.created_at.desc()).limit(10)

            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [r.value for r in rows if r.value]
        except Exception as e:
            logger.error(f"❌ Memory get_project_context error: {e}")
            return []

    async def save_project_context(
        self,
        project_id: str | None = None,
        project_name: str | None = None,
        agent_name: str = "",
        task_type: str = "",
        content: str = "",
        session: AsyncSession = None
    ):
        if content and len(content.strip()) > 20:
            try:
                values = dict(
                    namespace=self.namespace,
                    agent_name=agent_name,
                    task_type=task_type,
                    key=f"{agent_name}:{task_type}:last",
                    value=content,
                )
                if project_id:
                    values["project_id"] = project_id
                if project_name:
                    values["project_name"] = project_name

                stmt = insert(Memory).values(**values)
                await session.execute(stmt)
                await session.commit()

                proj_id_or_name = project_name or project_id or "unknown"
                logger.success(
                    f"🧠 Project memory stored for {agent_name}:{task_type} in project {proj_id_or_name}"
                )
            except Exception as e:
                logger.error(f"❌ Memory save_project_context error: {e}")
        else:
            logger.info("📭 Output not valuable enough to store.")
