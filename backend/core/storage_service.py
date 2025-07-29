import os
import re
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from backend.config.supabase_client import get_supabase_admin_client
from backend.config.envs import SUPABASE_URL
from supabase import Client

# Configure logging
logger = logging.getLogger(__name__)

class StorageService:
    """
    Comprehensive Supabase Storage service for managing resume and cover letter files.
    Implements hierarchical bucket organization and provides dual storage alongside local files.
    """
    
    BUCKET_NAME = "zumud-documents"
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self._initialize_client()
        
    def _initialize_client(self) -> None:
        """Initialize Supabase client with error handling."""
        try:
            self.supabase = get_supabase_admin_client()
            if self.supabase and SUPABASE_URL:
                self._ensure_bucket_exists()
                logger.info("Storage service initialized successfully")
            else:
                logger.warning("Supabase client not available - storage service will be disabled")
        except Exception as e:
            logger.error(f"Failed to initialize storage service: {e}")
            self.supabase = None
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure the main bucket exists, create if necessary."""
        if not self.supabase:
            return
            
        try:
            # Check if bucket exists
            response = self.supabase.storage.get_bucket(self.BUCKET_NAME)
            if response:
                logger.debug(f"Bucket {self.BUCKET_NAME} already exists")
                return
        except Exception as e:
            # If bucket doesn't exist (404), we'll try to create it
            # If it's another error, we'll still try to create it as a fallback
            logger.debug(f"Bucket {self.BUCKET_NAME} not found, attempting to create: {e}")
        
        # Try to create the bucket
        try:
            # Try the correct Supabase storage API format
            response = self.supabase.storage.create_bucket(
                self.BUCKET_NAME,  # bucket id/name as first parameter
                {"public": False, "file_size_limit": None, "allowed_mime_types": None}
            )
            if response:
                logger.info(f"Successfully created bucket {self.BUCKET_NAME}")
            else:
                logger.warning(f"Failed to create bucket {self.BUCKET_NAME}: No response from Supabase")
        except Exception as create_error:
            # If that fails, try alternative format
            try:
                logger.debug(f"First attempt failed, trying alternative format: {create_error}")
                response = self.supabase.storage.create_bucket({
                    "id": self.BUCKET_NAME,
                    "name": self.BUCKET_NAME,
                    "public": False
                })
                if response:
                    logger.info(f"Successfully created bucket {self.BUCKET_NAME} (alternative format)")
                else:
                    logger.warning(f"Failed to create bucket {self.BUCKET_NAME}: No response from Supabase (alternative format)")
            except Exception as final_error:
                logger.error(f"Failed to create bucket {self.BUCKET_NAME} with both methods: {create_error} | {final_error}")
    
    def _sanitize_company_name(self, company_name: str) -> str:
        """
        Sanitize company name for use in file paths and names.
        
        Args:
            company_name: Raw company name from job description
            
        Returns:
            Sanitized company name safe for file systems and cloud storage
        """
        if not company_name:
            return "unknown_company"
            
        # Convert to lowercase and replace spaces with underscores
        sanitized = company_name.lower().strip()
        
        # Remove or replace special characters that might cause issues
        # Keep alphanumeric, underscores, hyphens, and periods
        sanitized = re.sub(r'[^a-z0-9._-]', '_', sanitized)
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            sanitized = "unknown_company"
            
        # Limit length to avoid path issues
        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip('_')
            
        return sanitized
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for application tracking."""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    
    def _construct_user_path(self, user_id: int, path_type: str, 
                           session_id: Optional[str] = None, 
                           company_name: Optional[str] = None) -> str:
        """
        Construct hierarchical path for user files following the bucket structure.
        
        Args:
            user_id: User ID
            path_type: 'resumes' for original resumes, 'applications' for job applications
            session_id: Session ID for applications
            company_name: Company name for applications
            
        Returns:
            Constructed path string
        """
        base_path = f"users/{user_id}/{path_type}"
        
        if path_type == "applications" and session_id and company_name:
            sanitized_company = self._sanitize_company_name(company_name)
            return f"{base_path}/{session_id}_{sanitized_company}"
        
        return base_path
    
    def _construct_filename(self, file_type: str, company_name: Optional[str] = None, 
                          timestamp: Optional[str] = None, extra_info: str = "") -> str:
        """
        Construct filename following the naming convention.
        
        Args:
            file_type: Type of file (resume, cover_letter, qa, etc.)
            company_name: Company name for job applications
            timestamp: Timestamp for versioning
            extra_info: Additional info for filename
            
        Returns:
            Constructed filename
        """
        if not timestamp:
            timestamp = self._get_timestamp()
            
        if company_name:
            sanitized_company = self._sanitize_company_name(company_name)
            filename = f"{file_type}_{sanitized_company}_{timestamp}"
        else:
            filename = f"{file_type}_{timestamp}"
            
        if extra_info:
            filename += f"_{extra_info}"
            
        return filename
    
    def upload_file(self, file_path: str, file_content: bytes, 
                   content_type: str = "application/pdf") -> bool:
        """
        Upload a file to Supabase storage.
        
        Args:
            file_path: Path within the bucket where file should be stored
            file_content: Binary content of the file
            content_type: MIME type of the file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.supabase:
            logger.debug("Supabase client not available, skipping upload")
            return False
            
        try:
            # Try the standard upload format
            response = self.supabase.storage.from_(self.BUCKET_NAME).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": content_type, "cache-control": "3600", "upsert": "true"}
            )
            
            if response:
                logger.debug(f"Successfully uploaded file to {file_path}")
                return True
            else:
                logger.warning(f"Upload response was empty for {file_path}")
                return False
                
        except Exception as e:
            # Try alternative format without file_options
            try:
                logger.debug(f"First upload attempt failed, trying alternative format: {e}")
                response = self.supabase.storage.from_(self.BUCKET_NAME).upload(
                    file_path,  # path as positional argument
                    file_content,  # file as positional argument
                    {"upsert": True}  # options as third parameter
                )
                
                if response:
                    logger.debug(f"Successfully uploaded file to {file_path} (alternative format)")
                    return True
                else:
                    logger.warning(f"Upload response was empty for {file_path} (alternative format)")
                    return False
                    
            except Exception as final_error:
                logger.error(f"Failed to upload file to {file_path} with both methods: {e} | {final_error}")
                return False
    
    def upload_original_resume(self, user_id: int, file_content: bytes, 
                             filename: Optional[str] = None) -> bool:
        """
        Upload an original resume file to user's resume folder.
        
        Args:
            user_id: User ID
            file_content: PDF content of the resume
            filename: Optional custom filename
            
        Returns:
            True if successful, False otherwise
        """
        if not filename:
            timestamp = self._get_timestamp()
            filename = f"original_resume_{timestamp}.pdf"
        elif not filename.endswith('.pdf'):
            filename += '.pdf'
            
        user_path = self._construct_user_path(user_id, "resumes")
        file_path = f"{user_path}/{filename}"
        
        return self.upload_file(file_path, file_content, "application/pdf")
    
    def upload_tailored_resume(self, user_id: int, session_id: str, company_name: str,
                             pdf_content: bytes, tex_content: Optional[str] = None,
                             json_content: Optional[str] = None) -> Dict[str, bool]:
        """
        Upload tailored resume files (PDF, TEX, JSON) for a job application.
        
        Args:
            user_id: User ID
            session_id: Application session ID
            company_name: Company name for the application
            pdf_content: PDF content of the tailored resume
            tex_content: LaTeX source content (optional)
            json_content: Structured resume JSON (optional)
            
        Returns:
            Dictionary with success status for each file type
        """
        results = {"pdf": False, "tex": False, "json": False}
        
        timestamp = self._get_timestamp()
        base_path = self._construct_user_path(user_id, "applications", session_id, company_name)
        
        # Upload PDF
        pdf_filename = self._construct_filename("resume", company_name, timestamp) + ".pdf"
        pdf_path = f"{base_path}/{pdf_filename}"
        results["pdf"] = self.upload_file(pdf_path, pdf_content, "application/pdf")
        
        # Upload TEX if provided
        if tex_content:
            tex_filename = self._construct_filename("resume", company_name, timestamp) + ".tex"
            tex_path = f"{base_path}/{tex_filename}"
            results["tex"] = self.upload_file(tex_path, tex_content.encode('utf-8'), "application/x-tex")
        
        # Upload JSON if provided
        if json_content:
            json_filename = self._construct_filename("resume", company_name, timestamp) + ".json"
            json_path = f"{base_path}/{json_filename}"
            results["json"] = self.upload_file(json_path, json_content.encode('utf-8'), "application/json")
        
        return results
    
    def upload_cover_letter(self, user_id: int, session_id: str, company_name: str,
                          text_content: str, pdf_content: Optional[bytes] = None) -> Dict[str, bool]:
        """
        Upload cover letter files (text and PDF) for a job application.
        
        Args:
            user_id: User ID
            session_id: Application session ID
            company_name: Company name for the application
            text_content: Plain text content of the cover letter
            pdf_content: PDF content of the cover letter (optional)
            
        Returns:
            Dictionary with success status for each file type
        """
        results = {"text": False, "pdf": False}
        
        timestamp = self._get_timestamp()
        base_path = self._construct_user_path(user_id, "applications", session_id, company_name)
        
        # Upload text file
        text_filename = self._construct_filename("cover_letter", company_name, timestamp) + ".txt"
        text_path = f"{base_path}/{text_filename}"
        results["text"] = self.upload_file(text_path, text_content.encode('utf-8'), "text/plain")
        
        # Upload PDF if provided
        if pdf_content:
            pdf_filename = self._construct_filename("cover_letter", company_name, timestamp) + ".pdf"
            pdf_path = f"{base_path}/{pdf_filename}"
            results["pdf"] = self.upload_file(pdf_path, pdf_content, "application/pdf")
        
        return results
    
    def upload_question_answer(self, user_id: int, session_id: str, company_name: str,
                             question: str, answer: str, is_updated: bool = False) -> bool:
        """
        Upload question-answer pair for a job application.
        
        Args:
            user_id: User ID
            session_id: Application session ID
            company_name: Company name for the application
            question: The application question
            answer: The answer to the question
            is_updated: Whether this is an updated version
            
        Returns:
            True if successful, False otherwise
        """
        timestamp = self._get_timestamp()
        base_path = self._construct_user_path(user_id, "applications", session_id, company_name)
        
        # Create content
        content = f"Question:\n{question}\n\nAnswer:\n{answer}\n"
        
        # Determine filename
        prefix = "qa_updated" if is_updated else "qa"
        filename = self._construct_filename(prefix, company_name, timestamp) + ".txt"
        
        # Upload to questions subfolder
        file_path = f"{base_path}/questions/{filename}"
        
        return self.upload_file(file_path, content.encode('utf-8'), "text/plain")
    
    def upload_anonymous_resume(self, session_id: str, company_name: str,
                              pdf_content: bytes, filename: Optional[str] = None) -> bool:
        """
        Upload anonymous resume to dedicated anonymous section.
        
        Args:
            session_id: Anonymous session ID
            company_name: Company name for the application
            pdf_content: PDF content of the resume
            filename: Optional custom filename
            
        Returns:
            True if successful, False otherwise
        """
        if not filename:
            timestamp = self._get_timestamp()
            sanitized_company = self._sanitize_company_name(company_name)
            filename = f"anonymous_resume_{sanitized_company}_{timestamp}.pdf"
        elif not filename.endswith('.pdf'):
            filename += '.pdf'
            
        file_path = f"anonymous/{session_id}/{filename}"
        
        return self.upload_file(file_path, pdf_content, "application/pdf")
    
    def get_session_info(self, username: str, company_name: str) -> Tuple[str, str]:
        """
        Get or create session information for a user-company combination.
        This method helps maintain session consistency across related operations.
        
        Args:
            username: Username for local path compatibility
            company_name: Company name for the application
            
        Returns:
            Tuple of (session_id, sanitized_company_name)
        """
        # For now, generate a new session ID each time
        # In a more advanced implementation, you might want to track active sessions
        session_id = self._generate_session_id()
        sanitized_company = self._sanitize_company_name(company_name)
        
        return session_id, sanitized_company
    
    def is_available(self) -> bool:
        """Check if the storage service is available and operational."""
        return self.supabase is not None and SUPABASE_URL is not None


# Global storage service instance
storage_service = StorageService()


def get_storage_service() -> StorageService:
    """Get the global storage service instance."""
    return storage_service


# Convenience functions for dual storage operations
def safe_upload_with_fallback(upload_func, *args, **kwargs) -> bool:
    """
    Safely attempt to upload to Supabase with fallback handling.
    
    Args:
        upload_func: Storage service upload function to call
        *args, **kwargs: Arguments to pass to the upload function
        
    Returns:
        True if successful, False if failed (but doesn't raise exceptions)
    """
    try:
        if not storage_service.is_available():
            logger.debug("Storage service not available, skipping cloud upload")
            return False
            
        return upload_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Cloud storage upload failed: {e}")
        return False


# Utility functions for path and filename operations
def extract_company_from_path(path: str) -> Optional[str]:
    """
    Extract company name from local application path.
    
    Args:
        path: Local application path (e.g., /Applications/user/2024-01-15_google)
        
    Returns:
        Company name if found, None otherwise
    """
    try:
        path_parts = Path(path).name.split('_')
        if len(path_parts) >= 2:
            # Return everything after the timestamp part
            return '_'.join(path_parts[1:])
    except Exception:
        pass
    return None


def extract_session_from_path(path: str) -> Optional[str]:
    """
    Extract session timestamp from local application path for cloud session mapping.
    
    Args:
        path: Local application path
        
    Returns:
        Session-compatible timestamp if found, None otherwise
    """
    try:
        path_parts = Path(path).name.split('_')
        if len(path_parts) >= 1:
            # Return the timestamp part which can serve as a session identifier
            return path_parts[0]
    except Exception:
        pass
    return None