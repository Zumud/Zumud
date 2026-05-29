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
# Base URL of the self-hosted latex-online compiler (aslushnikov/latex-online).
# Defaults to localhost so production VPS deployments work without any extra config;
# override LATEX_COMPILER_BASE_URL in .env for local dev (e.g. point at a remote VPS).
LATEX_COMPILER_BASE_URL = getenv("LATEX_COMPILER_BASE_URL", "http://127.0.0.1:2700")
LaTeX_COMPILER_URL_DATA = LATEX_COMPILER_BASE_URL + "/data?target={tex_folder_path}&force=true&command={compiler}"

# Supabase Configuration
SUPABASE_URL = getenv("SUPABASE_URL")

# API keys. Supabase deprecated the JWT-based anon/service_role keys in favour of
# publishable (sb_publishable_...) and secret (sb_secret_...) keys. Prefer the new
# keys; fall back to the legacy names so the app keeps working during migration.
# https://supabase.com/docs/guides/getting-started/api-keys
SUPABASE_PUBLISHABLE_KEY = getenv("SUPABASE_PUBLISHABLE_KEY") or getenv("SUPABASE_ANON_KEY")
SUPABASE_SECRET_KEY = getenv("SUPABASE_SECRET_KEY") or getenv("SUPABASE_SERVICE_ROLE_KEY")

DATABASE_URL = getenv("DATABASE_URL")  # PostgreSQL connection string

# Validate required Supabase environment variables
if not DATABASE_URL:
    logger.error("DATABASE_URL is required for Supabase connection")
    raise ValueError("DATABASE_URL environment variable is required")

if not SUPABASE_URL:
    logger.warning("SUPABASE_URL not found in environment variables")

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
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))

# Stripe Configuration
# We do not log or hardcode keys here. Values must come from the environment (.env).
STRIPE_API_KEY = getenv("STRIPE_API_KEY") or getenv("STRIPE_SECRET_KEY")
STRIPE_COVERLETTER_PRICE_ID = getenv("STRIPE_COVERLETTER_PRICE_ID")
STRIPE_COVERLETTER_PRODUCT_NAME = getenv("STRIPE_COVERLETTER_PRODUCT_NAME", "CoverLetter Generation")
STRIPE_COVERLETTER_METER_NAME = getenv("STRIPE_COVERLETTER_METER_NAME", "coverletter_event")

# Additional products/meters
STRIPE_RESUME_PRICE_ID = getenv("STRIPE_RESUME_PRICE_ID")
STRIPE_RESUME_PRODUCT_NAME = getenv("STRIPE_RESUME_PRODUCT_NAME", "Resume Generation")
STRIPE_RESUME_METER_NAME = getenv("STRIPE_RESUME_METER_NAME", "resume_event")

STRIPE_QA_PRICE_ID = getenv("STRIPE_QA_PRICE_ID")
STRIPE_QA_PRODUCT_NAME = getenv("STRIPE_QA_PRODUCT_NAME", "Q&A Generation")
STRIPE_QA_METER_NAME = getenv("STRIPE_QA_METER_NAME", "qa_event")

STRIPE_COVERLETTER_EDIT_PRICE_ID = getenv("STRIPE_COVERLETTER_EDIT_PRICE_ID")
STRIPE_COVERLETTER_EDIT_PRODUCT_NAME = getenv("STRIPE_COVERLETTER_EDIT_PRODUCT_NAME", "CoverLetter Edit Generation")
STRIPE_COVERLETTER_EDIT_METER_NAME = getenv("STRIPE_COVERLETTER_EDIT_METER_NAME", "coverletter_edit_event")

STRIPE_RESUME_EDIT_PRICE_ID = getenv("STRIPE_RESUME_EDIT_PRICE_ID")
STRIPE_RESUME_EDIT_PRODUCT_NAME = getenv("STRIPE_RESUME_EDIT_PRODUCT_NAME", "Resume Edit Generation")
STRIPE_RESUME_EDIT_METER_NAME = getenv("STRIPE_RESUME_EDIT_METER_NAME", "resume_edit_event")

STRIPE_QA_EDIT_PRICE_ID = getenv("STRIPE_QA_EDIT_PRICE_ID")
STRIPE_QA_EDIT_PRODUCT_NAME = getenv("STRIPE_QA_EDIT_PRODUCT_NAME", "Q&A Edit Generation")
STRIPE_QA_EDIT_METER_NAME = getenv("STRIPE_QA_EDIT_METER_NAME", "qa_edit_event")

# Environment Configuration
ENVIRONMENT = getenv("ENVIRONMENT", "development")

# Frontend URL Configuration
# Automatically determine the correct frontend URL based on environment
if ENVIRONMENT.lower() == "production":
    FRONTEND_URL = getenv("FRONTEND_URL", "https://zumud.com")
else:
    FRONTEND_URL = getenv("FRONTEND_URL", "http://localhost:3000")

# Customer Portal Return URL
CUSTOMER_PORTAL_RETURN_URL = f"{FRONTEND_URL}/dashboard"

