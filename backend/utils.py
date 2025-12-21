from loguru import logger
import sys
from config.settings import settings

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)

logger.add(
    "logs/app_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level
)

def get_logger(name: str):
    return logger.bind(name=name)
