import os
import sys
import logging
import re
from loguru import logger
from backend.config.config import (
    LOG_FOLDER,
    LOG_LEVEL,
    LOG_FORMAT,
    NOISY_LIBRARY_LOGGERS,
)

# `diagnose=True` causes loguru to inline every local variable into tracebacks.
# That is helpful in development but in production it can dump secrets (tokens,
# passwords) into log files and bloat them. Off by default; opt in with
# LOG_DIAGNOSE=1.
DIAGNOSE = os.getenv("LOG_DIAGNOSE", "0") == "1"

# Create log directory
os.makedirs(LOG_FOLDER, exist_ok=True)

# Configure loguru
logger.remove()  # Remove default handler

# Add file handler
logger.add(
    os.path.join(LOG_FOLDER, "app_{time:YYYYMMDD_HHmmss}.log"),
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    rotation="10 MB",
    retention="1 week",
    compression="gz",
    backtrace=True,
    diagnose=DIAGNOSE,
    enqueue=True,  # write off the request thread so a slow disk can't stall the API
)

# Add console handler
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    backtrace=True,
    diagnose=DIAGNOSE,
    enqueue=True,
)

# Intercept standard library logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
            
        logger.opt(
            depth=6,
            exception=record.exc_info
        ).log(level, record.getMessage())

# Configure standard library logging
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Configure external loggers
for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
    logging.getLogger(name).handlers = [InterceptHandler()]
    logging.getLogger(name).propagate = False

# Force noisy libraries (httpx/httpcore/hpack/...) up to WARNING regardless of
# the global LOG_LEVEL. These emit per-request hex dumps that destroy log disks
# and obscure real errors.
for name in NOISY_LIBRARY_LOGGERS:
    logging.getLogger(name).setLevel(logging.WARNING)

# Capture stdout/stderr
class SmartCaptureHandler:
    def __init__(self, default_level="INFO", original_stream=None):
        self.default_level = default_level
        self.original_stream = original_stream
        self.level_patterns = {
            "DEBUG": re.compile(r'\bDEBUG\b'),
            "INFO": re.compile(r'\bINFO\b'),
            "WARNING": re.compile(r'\b(WARN(ING)?)\b'),
            "ERROR": re.compile(r'\bERROR\b'),
            "CRITICAL": re.compile(r'\b(CRIT(ICAL)?|FATAL)\b'),
        }
    
    def detect_level(self, message):
        for level, pattern in self.level_patterns.items():
            if pattern.search(message):
                return level
        return self.default_level
    
    def write(self, message):
        if message and not message.isspace():
            level = self.detect_level(message)
            logger.opt(depth=0).log(level, message.rstrip())
        if self.original_stream:
            self.original_stream.write(message)
            
    def flush(self):
        if self.original_stream:
            self.original_stream.flush()
            
    def __getattr__(self, name):
        if self.original_stream:
            return getattr(self.original_stream, name)
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

# Replace stdout/stderr
sys.stdout = SmartCaptureHandler("INFO", sys.stdout)
sys.stderr = SmartCaptureHandler("ERROR", sys.stderr)