from os import getenv
from dotenv import load_dotenv
import secrets
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

OPEN_AI_KEY = getenv("OPEN_AI_KEY")  # Put your open AI key here
GMAIL_APP_PASSWORD = getenv("GMAIL_APP_PASSWORD")  # Put your gmail app password here
ADD_GDRIVE_ZAP_URL = getenv("ADD_GDRIVE_ZAP_URL")  # Put zappier webhook workflow here, This webhook uploads the file to GDrive
LaTeX_COMPILER_URL_TEXT = "https://texlive2020.latexonline.cc/compile?command=pdflatex&text="
LaTeX_COMPILER_URL_DATA = "https://texlive2020.latexonline.cc/data?target={tex_folder_path}&force=true&command={compiler}"

# If SECRET_KEY is not provided in environment, generate a secure random one
# Note: This will cause all JWTs to be invalidated when the server restarts
# For production use, set a permanent SECRET_KEY in your .env file
SECRET_KEY = getenv("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    logger.warning(
        "No SECRET_KEY found in environment variables. "
        "Generated a random key for this session. "
        "All users will need to re-login after server restart. "
        "For production, set a permanent SECRET_KEY in your .env file."
    )

ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))

