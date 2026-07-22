import logging
from os import getenv

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

OPEN_AI_KEY = getenv("OPEN_AI_KEY")  # Put your open AI key here

# Base URL of the self-hosted latex-online compiler (aslushnikov/latex-online).
# Defaults to localhost so production VPS deployments work without any extra config;
# override LATEX_COMPILER_BASE_URL in .env for local dev (e.g. point at a remote VPS).
LATEX_COMPILER_BASE_URL = getenv("LATEX_COMPILER_BASE_URL", "http://127.0.0.1:2700")
LaTeX_COMPILER_URL_DATA = (
    LATEX_COMPILER_BASE_URL
    + "/data?target={tex_folder_path}&force=true&command={compiler}"
)

# Supabase Configuration
SUPABASE_URL = getenv("SUPABASE_URL")

# API key. Supabase deprecated the JWT-based service_role key in favour of the
# secret (sb_secret_...) key. Prefer the new key; fall back to the legacy name
# so the app keeps working during migration.
# https://supabase.com/docs/guides/getting-started/api-keys
SUPABASE_SECRET_KEY = getenv("SUPABASE_SECRET_KEY") or getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

# Used to verify Supabase Auth (GoTrue) access tokens signed with the legacy
# symmetric (HS256) project JWT secret. For projects using asymmetric signing
# keys (ES256/RS256) this can be left unset; tokens are then verified against
# the project JWKS endpoint derived from SUPABASE_URL.
SUPABASE_JWT_SECRET = getenv("SUPABASE_JWT_SECRET")

DATABASE_URL = getenv("DATABASE_URL")  # PostgreSQL connection string

# Validate required Supabase environment variables
if not DATABASE_URL:
    logger.error("DATABASE_URL is required for Supabase connection")
    raise ValueError("DATABASE_URL environment variable is required")

if not SUPABASE_URL:
    logger.warning("SUPABASE_URL not found in environment variables")

# Stripe Configuration
# We do not log or hardcode keys here. Values must come from the environment (.env).
STRIPE_API_KEY = getenv("STRIPE_API_KEY") or getenv("STRIPE_SECRET_KEY")
STRIPE_COVERLETTER_PRICE_ID = getenv("STRIPE_COVERLETTER_PRICE_ID")
STRIPE_COVERLETTER_PRODUCT_NAME = getenv(
    "STRIPE_COVERLETTER_PRODUCT_NAME", "CoverLetter Generation"
)
STRIPE_COVERLETTER_METER_NAME = getenv(
    "STRIPE_COVERLETTER_METER_NAME", "coverletter_event"
)

# Additional products/meters
STRIPE_RESUME_PRICE_ID = getenv("STRIPE_RESUME_PRICE_ID")
STRIPE_RESUME_PRODUCT_NAME = getenv("STRIPE_RESUME_PRODUCT_NAME", "Resume Generation")
STRIPE_RESUME_METER_NAME = getenv("STRIPE_RESUME_METER_NAME", "resume_event")

STRIPE_QA_PRICE_ID = getenv("STRIPE_QA_PRICE_ID")
STRIPE_QA_PRODUCT_NAME = getenv("STRIPE_QA_PRODUCT_NAME", "Q&A Generation")
STRIPE_QA_METER_NAME = getenv("STRIPE_QA_METER_NAME", "qa_event")

STRIPE_COVERLETTER_EDIT_PRICE_ID = getenv("STRIPE_COVERLETTER_EDIT_PRICE_ID")
STRIPE_COVERLETTER_EDIT_PRODUCT_NAME = getenv(
    "STRIPE_COVERLETTER_EDIT_PRODUCT_NAME", "CoverLetter Edit Generation"
)
STRIPE_COVERLETTER_EDIT_METER_NAME = getenv(
    "STRIPE_COVERLETTER_EDIT_METER_NAME", "coverletter_edit_event"
)

STRIPE_RESUME_EDIT_PRICE_ID = getenv("STRIPE_RESUME_EDIT_PRICE_ID")
STRIPE_RESUME_EDIT_PRODUCT_NAME = getenv(
    "STRIPE_RESUME_EDIT_PRODUCT_NAME", "Resume Edit Generation"
)
STRIPE_RESUME_EDIT_METER_NAME = getenv(
    "STRIPE_RESUME_EDIT_METER_NAME", "resume_edit_event"
)

STRIPE_QA_EDIT_PRICE_ID = getenv("STRIPE_QA_EDIT_PRICE_ID")
STRIPE_QA_EDIT_PRODUCT_NAME = getenv(
    "STRIPE_QA_EDIT_PRODUCT_NAME", "Q&A Edit Generation"
)
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
