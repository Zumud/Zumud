import os
import sys
import logging
import re
from loguru import logger
from backend.config.config import LOG_FOLDER, LOG_LEVEL, LOG_FORMAT

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
    backtrace=True,
    diagnose=False  # do NOT inline local variables into tracebacks (would leak secrets)
)

# Add console handler
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    backtrace=True,
    diagnose=False  # do NOT inline local variables into tracebacks (would leak secrets)
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