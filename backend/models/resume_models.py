from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ResumeBase(BaseModel):
    resume_content: Optional[str] = None

class Resume(ResumeBase):
    last_updated: datetime

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models

# AI Response Models
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
    role: Optional[str] = None
    location: Optional[str] = None
    date_range: Optional[str] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None

class Education(BaseModel):
    institution: str
    degree: Optional[str] = None
    location: Optional[str] = None
    date_range: Optional[str] = None
    minors: Optional[List[str]] = None

class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None

class Project(BaseModel):
    name: str
    date_range: Optional[str] = None
    achievements: Optional[List[str]] = None

class PersonalInfo(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

class Award(BaseModel):
    title: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None

class Publication(BaseModel):
    title: str
    authors: Optional[str] = None
    venue: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    date: Optional[str] = None
    status: Optional[str] = None  # For "Under Review", "In Press", "Forthcoming", "Submitted"
    doi: Optional[str] = None
    url: Optional[str] = None

class StructuredResume(BaseModel):
    personal_info: PersonalInfo
    summary: Optional[str] = None
    skills: Optional[List[ResumeSection]] = None
    experience: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None
    certifications: Optional[List[Certification]] = None
    projects: Optional[List[Project]] = None
    publications: Optional[List[Publication]] = None
    awards: Optional[List[Award]] = None