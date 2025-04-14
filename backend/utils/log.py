import os
import sys
import logging
import datetime
from loguru import logger

from backend.config.config import LOG_LEVEL, LOG_TO_CONSOLE, LOG_TO_FOLDER, LOG_FOLDER, LOG_FORMAT

def remove_default_loggers():
    """Remove all handlers from the root logger."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()     # Clear all handlers from the root logger

def init_loguru_logger():
    """
    Configure the Loguru logger for file and console logging.

    - Creates the log directory if needed.
    - Removes existing Loguru handlers.
    - Adds a file logger with timestamped filename if `LOG_TO_FOLDER` is enabled.
    - Adds a console logger for real-time output if `LOG_TO_CONSOLE` is enabled.
    
    Global Variables:
    - `LOG_FOLDER`: Path to the folder where logs will be stored.
    - `LOG_TO_FOLDER`: Enable/disable file logging.
    - `LOG_TO_CONSOLE`: Enable/disable console logging.
    - `LOG_LEVEL`: Logging verbosity level.
    """
    # Ensure log directory exists
    os.makedirs(LOG_FOLDER, exist_ok=True)

    # Create a timestamp for the log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_FOLDER, f"app_{timestamp}.log")

    logger.remove()

    # Add file logger if LOG_TO_FOLDER is True
    if LOG_TO_FOLDER:
        logger.add(
            log_file,
            level=LOG_LEVEL,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
            format=LOG_FORMAT,
            backtrace=True,
            diagnose=True,
        )

    # Add console logger if LOG_TO_CONSOLE is True
    if LOG_TO_CONSOLE:
        logger.add(
            sys.stderr,
            level=LOG_LEVEL,
            format=LOG_FORMAT,
            backtrace=True,
            diagnose=True,
        )

remove_default_loggers()
init_loguru_logger()