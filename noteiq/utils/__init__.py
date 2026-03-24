"""
Logging utilities for NoteIQ
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional


# Log levels
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"


class NoteIQLogger:
    """Custom logger for NoteIQ application"""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "noteiq", level: str = INFO) -> logging.Logger:
        """
        Get or create a logger instance.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        Returns:
            Configured logger instance
        """
        if cls._instance is not None:
            return cls._instance
        
        logger = logging.getLogger(name)
        
        # Set level
        level_map = {
            DEBUG: logging.DEBUG,
            INFO: logging.INFO,
            WARNING: logging.WARNING,
            ERROR: logging.ERROR,
            CRITICAL: logging.CRITICAL
        }
        logger.setLevel(level_map.get(level, logging.INFO))
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level_map.get(level, logging.INFO))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler
        logger.addHandler(handler)
        
        cls._instance = logger
        return logger


# Default logger instance
logger = NoteIQLogger.get_logger()


def log_debug(message: str):
    """Log debug message"""
    logger.debug(message)


def log_info(message: str):
    """Log info message"""
    logger.info(message)


def log_warning(message: str):
    """Log warning message"""
    logger.warning(message)


def log_error(message: str, exc_info: bool = False):
    """Log error message"""
    logger.error(message, exc_info=exc_info)


def log_critical(message: str):
    """Log critical message"""
    logger.critical(message)