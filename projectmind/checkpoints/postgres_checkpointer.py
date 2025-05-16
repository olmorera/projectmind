# checkpoints/postgres_checkpointer.py

from langgraph.checkpoint.postgres import PostgresSaver
from loguru import logger

def get_postgres_checkpointer():
    from projectmind.config import settings  # asegúrate que DATABASE_URL esté aquí

    try:
        checkpointer = PostgresSaver.from_conn_string(settings.DATABASE_URL)
        checkpointer.setup()  # crea las tablas necesarias
        logger.info("✅ Postgres checkpointer initialized successfully")
        return checkpointer
    except Exception as e:
        logger.error(f"❌ Failed to initialize Postgres checkpointer: {e}")
        raise
