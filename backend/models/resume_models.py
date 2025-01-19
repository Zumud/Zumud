from pydantic import BaseModel
from datetime import datetime

class ResumeBase(BaseModel):
    resume_content: str

class Resume(ResumeBase):
    last_updated: datetime

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models