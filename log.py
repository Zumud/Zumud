import os
import sys
import time
import logging
from loguru import logger

from config import LOG_LEVEL, LOG_TO_CONSOLE, LOG_TO_FILE, LOG_FILE, LOG_FORMAT

log_file = LOG_FILE

def remove_default_loggers():
    """Remove all handlers from the root logger and delete the log file if it exists."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()     # Clear all handlers from the root logger

    # Remove the log file if it exists
    try:
        os.remove(log_file)
    except FileNotFoundError:
        pass  # File does not exist, no action needed

def init_loguru_logger():
    """
    Configure the Loguru logger for file and console logging.

    - Creates the directory for log files if needed.
    - Removes existing Loguru handlers.
    - Adds a file logger if `LOG_TO_FILE` is enabled.
    - Adds a console logger for real-time output if `LOG_TO_CONSOLE` is enabled.
    
    Global Variables:
    - `log_file`: Path to the log file.
    - `LOG_TO_FILE`: Enable/disable file logging.
    - `LOG_TO_CONSOLE`: Enable/disable console logging.
    - `LOG_LEVEL`: Logging verbosity level.
    """

    # Make a log file in the LOG_FILE path
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger.remove()

    # Add file logger if LOG_TO_FILE is True
    if LOG_TO_FILE:
        logger.add(
            log_file,
            level=LOG_LEVEL,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
            format= LOG_FORMAT,
            backtrace=True,
            diagnose=True,
        )

    # Add console logger if LOG_TO_CONSOLE is True
    if LOG_TO_CONSOLE:
        logger.add(
            sys.stderr,
            level=LOG_LEVEL,
            format= LOG_FORMAT,
            backtrace=True,
            diagnose=True,
        )

remove_default_loggers()
init_loguru_logger()