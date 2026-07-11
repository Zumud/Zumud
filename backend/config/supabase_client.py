import logging

from backend.config.envs import (
    SUPABASE_PUBLISHABLE_KEY,
    SUPABASE_SECRET_KEY,
    SUPABASE_URL,
)
from supabase import Client, create_client

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Supabase clients
supabase_client: Client = None
supabase_admin_client: Client = None


def get_supabase_client() -> Client:
    """Get Supabase client with the publishable key (for public/anon-scoped operations)."""
    global supabase_client

    if not supabase_client and SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY:
        try:
            supabase_client = create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")

    return supabase_client


def get_supabase_admin_client() -> Client:
    """Get Supabase admin client with the secret key (bypasses RLS; backend only)."""
    global supabase_admin_client

    if not supabase_admin_client and SUPABASE_URL and SUPABASE_SECRET_KEY:
        try:
            supabase_admin_client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
            logger.info("Supabase admin client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase admin client: {e}")

    return supabase_admin_client
