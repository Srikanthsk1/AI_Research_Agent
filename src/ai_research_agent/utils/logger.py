import sys
import os
from dotenv import load_dotenv

from loguru import logger


load_dotenv()
os.makedirs("logs", exist_ok=True)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logger.remove()

# Console logs
logger.add(
    sys.stdout,
    level=log_level,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
)

# File logs
logger.add(
    "logs/research_agent.log",
    level=log_level,
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level} | "
        "{name}:{function}:{line} | "
        "{message}"
    ),
)
