from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ResumeBase(BaseModel):
    resume_content: str

class Resume(ResumeBase):
    last_updated: datetime

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models

# AI Response Models
class Eligibility(BaseModel):
    eligibility: bool = Field(..., description="Indicates eligibility: 'True' or 'False'.")
    reason: str = Field(..., description="Explanation of eligibility")

class Suitability(BaseModel):
    suitability: bool = Field(..., description="Indicates suitability: 'True' or 'False'.")
    reason: str = Field(..., description="Explanation of suitability")

class TailoredResume(BaseModel):
    tailored_resume: str

class TailoredCoverLetter(BaseModel):
    tailored_coverletter: str

class CustomizedResume(BaseModel):
    customized_resume: str

class TailoredCL(BaseModel):
    customized_cover_letter: str

class CompanyName(BaseModel):
    company_name: str

class TailoredAnswer(BaseModel):
    tailored_answer: str

# Resume Structure Models
class ResumeSection(BaseModel):
    category: str
    items: List[str]

class Experience(BaseModel):
    company: str
    role: str
    location: str
    date_range: str
    description: Optional[str] = None
    achievements: List[str]

class Education(BaseModel):
    institution: str
    degree: str
    location: str
    date_range: str
    minors: Optional[List[str]] = None

class Certification(BaseModel):
    name: str
    issuer: str

class Project(BaseModel):
    name: str
    date_range: str
    achievements: List[str]

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    linkedin: str
    github: str

class Award(BaseModel):
    title: str
    issuer: str
    date: str
    description: Optional[str] = None

class StructuredResume(BaseModel):
    personal_info: PersonalInfo
    summary: str
    skills: List[ResumeSection]
    experience: List[Experience]
    education: List[Education]
    certifications: Optional[List[Certification]] = None
    projects: Optional[List[Project]] = None
    awards: Optional[List[Award]] = None