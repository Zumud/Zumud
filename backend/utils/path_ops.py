import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from backend.config.config import APPLICATIONS_DIR


# Application context to track the current application folder
class ApplicationContext:
    """
    Singleton class to manage the current application context per user.
    This ensures all documents for a single job application are saved in the same folder,
    and different users have separate contexts.
    """
    _instance = None
    _user_application_paths: Dict[str, Path] = {}

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
    def clear_current_path(cls, username: str):
        """
        Clear the current application path for a specific user
        
        Args:
            username: Username for which to clear the current path
        """
        if username in cls._user_application_paths:
            del cls._user_application_paths[username]


def create_new_application_path(username: str, company_name: str, timestamp: Optional[str] = None) -> Path:
    """
    Create a new application path for a company under a specific user.
    This always creates a new path and sets it as the current application context for that user.
    
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
    
    return path


def get_current_application_path(username: str, company_name: Optional[str] = None) -> Path:
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