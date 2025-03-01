import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config.config import APPLICATIONS_DIR


# Application context to track the current application folder
class ApplicationContext:
    """
    Singleton class to manage the current application context.
    This ensures all documents for a single job application are saved in the same folder.
    """
    _instance = None
    _current_application_path = None

    def __new__(cls):
        # Check if an instance of this class already exists
        if cls._instance is None:
            # If no instance exists, create a new one using the parent class's __new__ method
            # This implements the Singleton pattern, ensuring only one instance of ApplicationContext exists
            cls._instance = super(ApplicationContext, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_current_path(cls) -> Optional[Path]:
        """Get the current application path if it exists"""
        return cls._current_application_path
    
    @classmethod
    def set_current_path(cls, path: Path):
        """Set the current application path"""
        cls._current_application_path = path
    
    @classmethod
    def clear_current_path(cls):
        """Clear the current application path"""
        cls._current_application_path = None


def create_new_application_path(company_name: str, timestamp: Optional[str] = None) -> Path:
    """
    Create a new application path for a company.
    This always creates a new path and sets it as the current application context.
    
    Args:
        company_name: Name of the company being applied to
        timestamp: Optional timestamp string, will generate one if not provided
        
    Returns:
        Path object for the new application directory
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    path = APPLICATIONS_DIR / f"{timestamp}_{company_name}"
    os.makedirs(path, exist_ok=True)
    
    # Set this as the current application context
    ApplicationContext.set_current_path(path)
    
    return path


def get_current_application_path(company_name: Optional[str] = None) -> Path:
    """
    Get the current application path if it exists, or create a new one if it doesn't.
    
    Args:
        company_name: Optional company name to use if creating a new path
        
    Returns:
        Path object for the application directory
    """
    current_path = ApplicationContext.get_current_path()
    
    if current_path is not None:
        return current_path
    
    # No current path exists, create a new one
    if company_name is None:
        company_name = "unknown_company"  # Default name if none provided
    
    return create_new_application_path(company_name)