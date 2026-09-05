import sys
from pathlib import Path
from loguru import logger
from typing import Optional

_logger_configured = False


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rotation: str = "1 day",
    retention: str = "7 days",
) -> None:
    """Setup logging configuration."""
    global _logger_configured
    
    if _logger_configured:
        return
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=rotation,
            retention=retention,
            level=level,
        )
    
    _logger_configured = True

def get_logger(name: str):
    """Get a logger instance."""
    if not _logger_configured:
        setup_logging()
    return logger.bind(name=name)
