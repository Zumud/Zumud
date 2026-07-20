import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from backend.config.config import APPLICATIONS_DIR


# Application context to track the current application folder
class ApplicationContext:
    """
    Singleton class to manage the current application context per user.
    This ensures all documents for a single job application are saved in the same folder,
    and different users have separate contexts.
    Enhanced with session tracking for cloud storage integration.
    """

    _instance = None
    _user_application_paths: Dict[str, Path] = {}
    _user_session_info: Dict[
        str, Tuple[str, str]
    ] = {}  # username -> (session_id, company_name)

    def __new__(cls):
        # Check if an instance of this class already exists
        if cls._instance is None:
            # If no instance exists, create a new one using the parent class's __new__ method
            # This implements the Singleton pattern, ensuring only one instance of ApplicationContext exists
            cls._instance = super(ApplicationContext, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_current_path(cls, username: str) -> Optional[Path]:
        """
        Get the current application path for a specific user if it exists

        Args:
            username: Username for which to get the current path
        """
        return cls._user_application_paths.get(username)

    @classmethod
    def set_current_path(cls, username: str, path: Path):
        """
        Set the current application path for a specific user

        Args:
            username: Username for which to set the current path
            path: Path to set
        """
        cls._user_application_paths[username] = path

    @classmethod
    def get_session_info(cls, username: str) -> Optional[Tuple[str, str]]:
        """
        Get the current session info (session_id, company_name) for a user.

        Args:
            username: Username for which to get session info

        Returns:
            Tuple of (session_id, company_name) if exists, None otherwise
        """
        return cls._user_session_info.get(username)

    @classmethod
    def set_session_info(cls, username: str, session_id: str, company_name: str):
        """
        Set session info for cloud storage tracking.

        Args:
            username: Username for which to set session info
            session_id: Session ID for cloud storage organization
            company_name: Company name for the application
        """
        cls._user_session_info[username] = (session_id, company_name)

    @classmethod
    def generate_session_id(cls) -> str:
        """Generate a unique session ID for application tracking."""
        return str(uuid.uuid4())


def create_new_application_path(
    username: str, company_name: str, timestamp: Optional[str] = None
) -> Path:
    """
    Create a new application path for a company under a specific user.
    This always creates a new path and sets it as the current application context for that user.
    Enhanced with session tracking for cloud storage integration.

    Args:
        username: Username of the user creating the application
        company_name: Name of the company being applied to
        timestamp: Optional timestamp string, will generate one if not provided

    Returns:
        Path object for the new application directory
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create the user directory if it doesn't exist
    user_dir = APPLICATIONS_DIR / username

    # Create the application directory
    path = user_dir / f"{timestamp}_{company_name}"
    os.makedirs(path, exist_ok=True)

    # Set this as the current application context for this user
    ApplicationContext.set_current_path(username, path)

    # Generate and store session info for cloud storage
    session_id = ApplicationContext.generate_session_id()
    ApplicationContext.set_session_info(username, session_id, company_name)

    return path


def get_current_application_path(
    username: str, company_name: Optional[str] = None
) -> Path:
    """
    Get the current application path for a user if it exists, or create a new one if it doesn't.

    Args:
        username: Username of the user
        company_name: Optional company name to use if creating a new path

    Returns:
        Path object for the application directory
    """
    current_path = ApplicationContext.get_current_path(username)

    if current_path is not None:
        return current_path

    # No current path exists, create a new one
    if company_name is None:
        company_name = "unknown_company"  # Default name if none provided

    return create_new_application_path(username, company_name)


def get_or_create_application(
    username: str, company_name: str, is_new_application: Optional[bool] = None
) -> Path:
    """
    Unified application management logic that handles the is_new_application flag.

    Args:
        username: Username of the user
        company_name: Name of the company being applied to
        is_new_application: Optional flag to control application creation:
            - True: Always create new application
            - False: Use existing if available, create new if none exists
            - None: Create new application (default for backward compatibility)

    Returns:
        Path object for the application directory
    """
    if is_new_application is True:
        # Explicit request for new application
        return create_new_application_path(username, company_name)

    # For is_new_application=False or None, try to reuse existing
    existing_path = ApplicationContext.get_current_path(username)

    if existing_path is not None:
        return existing_path

    # No existing application, create new one
    return create_new_application_path(username, company_name)


def get_current_session_info(username: str) -> Optional[Tuple[str, str]]:
    """
    Get the current session information for cloud storage operations.

    Args:
        username: Username of the user

    Returns:
        Tuple of (session_id, company_name) if available, None otherwise
    """
    return ApplicationContext.get_session_info(username)


def extract_company_from_local_path(path: Path) -> Optional[str]:
    """
    Extract company name from local application path.

    Args:
        path: Local application path

    Returns:
        Company name if found, None otherwise
    """
    try:
        path_parts = path.name.split("_")
        if len(path_parts) >= 2:
            # Return everything after the timestamp part
            return "_".join(path_parts[1:])
    except Exception:
        pass
    return None


def create_session_aware_path(
    username: str,
    company_name: str,
    session_id: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Tuple[Path, str, str]:
    """
    Create a new application path with explicit session tracking.
    This is useful when you need to coordinate local and cloud storage operations.

    Args:
        username: Username of the user creating the application
        company_name: Name of the company being applied to
        session_id: Optional explicit session ID (generates one if not provided)
        timestamp: Optional timestamp string (generates one if not provided)

    Returns:
        Tuple of (local_path, session_id, sanitized_company_name)
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if session_id is None:
        session_id = ApplicationContext.generate_session_id()

    # Create the user directory if it doesn't exist
    user_dir = APPLICATIONS_DIR / username

    # Create the application directory
    path = user_dir / f"{timestamp}_{company_name}"
    os.makedirs(path, exist_ok=True)

    # Set this as the current application context for this user
    ApplicationContext.set_current_path(username, path)
    ApplicationContext.set_session_info(username, session_id, company_name)

    return path, session_id, company_name
