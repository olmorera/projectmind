# projectmind/db/models/__init__.py

from projectmind.db.models.base import Base
from projectmind.db.models.prompt import Prompt
from projectmind.db.models.task import Task
from projectmind.db.models.agent import Agent
from projectmind.db.models.agent_run import AgentRun
from projectmind.db.models.memory import Memory  # ✅ necesario para que Alembic lo detecte

__all__ = ["Base", "Prompt", "Task", "Agent", "AgentRun", "Memory"]
