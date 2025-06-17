from supabase import create_client, Client
from backend.config.envs import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Supabase clients
supabase_client: Client = None
supabase_admin_client: Client = None

def get_supabase_client() -> Client:
    """Get Supabase client with anon key (for public operations)."""
    global supabase_client
    
    if not supabase_client and SUPABASE_URL and SUPABASE_ANON_KEY:
        try:
            supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
    
    return supabase_client

def get_supabase_admin_client() -> Client:
    """Get Supabase admin client with service role key (for admin operations)."""
    global supabase_admin_client
    
    if not supabase_admin_client and SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            supabase_admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Supabase admin client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase admin client: {e}")
    
    return supabase_admin_client 