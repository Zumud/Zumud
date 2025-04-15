# In this file, you can set the configurations of the app.
import os
from pathlib import Path

# Logging configuration
LOG_FOLDER = "log"
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# File paths configuration
BASE_DIR = Path(".")
APPLICATIONS_DIR = BASE_DIR / "Applications"
TEX_FILE_NAME = "resume"
TAR_FOLDER_NAME = "resume"

# Ensure directories exist
os.makedirs(APPLICATIONS_DIR, exist_ok=True)
