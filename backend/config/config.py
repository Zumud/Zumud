# In this file, you can set the configurations of the app.
import os
from pathlib import Path

# Logging configuration
# LOG_LEVEL is env-driven so production can run at INFO/WARNING without
# changing code. Default is INFO; only opt into DEBUG locally.
LOG_FOLDER = os.getenv("LOG_FOLDER", "log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Libraries that emit extremely chatty DEBUG output (per-request hex dumps).
# We force these to WARNING regardless of LOG_LEVEL to keep disk usage sane.
NOISY_LIBRARY_LOGGERS = (
    "httpx",
    "httpcore",
    "hpack",
    "h2",
    "urllib3",
    "asyncio",
    "passlib",
    "multipart",
    "sqlalchemy.engine",
)

# File paths configuration
BASE_DIR = Path(".")
APPLICATIONS_DIR = BASE_DIR / "Applications"
TEX_FILE_NAME = "resume"
TAR_FOLDER_NAME = "resume"

# Ensure directories exist
os.makedirs(APPLICATIONS_DIR, exist_ok=True)
