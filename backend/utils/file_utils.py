import base64
import datetime
import os
import uuid
from pathlib import Path
from typing import Optional

# Set up uploads directory - using a relative path from the root
UPLOADS_DIR = Path("./uploads/resumes")


def ensure_upload_directory():
    """Ensure the uploads directory exists"""
    os.makedirs(UPLOADS_DIR, exist_ok=True)


def save_base64_pdf(base64_data: str) -> Optional[str]:
    """
    Saves a base64 encoded PDF file to the uploads directory.

    Args:
        base64_data: Base64 encoded PDF data

    Returns:
        Path to the saved file or None if saving failed
    """
    if not base64_data:
        return None

    try:
        # Remove potential data URI prefix
        if "base64," in base64_data:
            base64_data = base64_data.split("base64,")[1]

        # Decode the base64 data
        pdf_data = base64.b64decode(base64_data)

        # Create a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create a unique filename with timestamp
        filename = f"{timestamp}_{uuid.uuid4()}.pdf"

        # Ensure directory exists
        ensure_upload_directory()

        # Full path to save the file
        file_path = UPLOADS_DIR / filename

        # Save the file
        with open(file_path, "wb") as f:
            f.write(pdf_data)

        return str(file_path)
    except Exception as e:
        print(f"Error saving PDF file: {e}")
        return None
