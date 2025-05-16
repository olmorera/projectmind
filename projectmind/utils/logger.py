# projectmind/utils/logger.py
from loguru import logger
import sys

logger.remove()  # Eliminar configuración por defecto
logger.add(sys.stdout, level="DEBUG", format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")
