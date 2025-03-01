# In this file, you can set the configurations of the app.
import streamlit as st
import os
from pathlib import Path

# Config related to log
LOG_LEVEL = "DEBUG"
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
LOG_FILE = "log/app.log"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
TEX_FILE_NAME = "resume"
TAR_FOLDER_NAME = "resume"

# File paths configuration
BASE_DIR = Path(".")
APPLICATIONS_DIR = BASE_DIR / "Applications"

# Ensure directories exist
os.makedirs(APPLICATIONS_DIR, exist_ok=True)
