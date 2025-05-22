from loguru import logger
from projectmind.tasks.task_manager import save_tasks_from_output


async def try_saving_tasks(session, project, agent_row, agent_name, output):
    if project and agent_row.can_create_tasks:
        try:
            await save_tasks_from_output(project.id, agent_name, output, session)
            logger.success(f"📝 Tasks saved by {agent_name}")
        except Exception as e:
            logger.error(f"❌ Error saving tasks: {e}")
