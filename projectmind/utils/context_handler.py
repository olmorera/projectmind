from projectmind.memory.memory_manager import MemoryManager
from loguru import logger


async def load_context(session, agent_row, agent, project, agent_name):
    if not (project and agent.definition.type and agent_row.use_memory):
        return ""
    memory = MemoryManager(namespace="task_outputs")
    context_items = await memory.get_project_context(
        project_id=project.id,
        agent_name=agent_name,
        task_type=agent.definition.type,
        session=session
    )
    logger.debug(f"📚 Retrieved {len(context_items)} context items")
    return "\n\n".join(context_items) if context_items else ""


async def save_context(session, agent_row, agent, project, agent_name, output):
    if not (project and agent.definition.type and agent_row.use_memory):
        return
    try:
        memory = MemoryManager(namespace="task_outputs")
        await memory.save_project_context(
            project_id=project.id,
            agent_name=agent_name,
            task_type=agent.definition.type,
            content=output,
            session=session
        )
        logger.success("🧠 Project memory stored")
    except Exception as e:
        logger.error(f"❌ Error saving project memory: {e}")
