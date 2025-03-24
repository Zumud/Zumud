from pydantic import BaseModel
from typing import Optional

class EligibilityResponse(BaseModel):
    eligibility: bool
    reason: str

class SuitabilityResponse(BaseModel):
    suitability: bool
    reason: str

class ApplicationResponse(BaseModel):
    success: str
    pdf_file_path: Optional[str] = None
    latex_code: Optional[str] = None 