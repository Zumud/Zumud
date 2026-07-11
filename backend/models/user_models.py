from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr


# Create/Update schemas
class UserCreate(UserBase):
    password: str
    initial_resume: Optional[str] = None
    resume_file: Optional[str] = None  # This will contain the base64 encoded file data


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models


class UserPreferenceCreate(BaseModel):
    preference: str


class UserPreference(BaseModel):
    preferences_text: str
    last_updated: datetime

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models


class Token(BaseModel):
    access_token: str
    token_type: str


class UserTemplateBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User-friendly name for the template",
    )
    latex_content: str = Field(
        ..., min_length=1, description="The LaTeX template content"
    )
    compiler: str = Field(
        default="pdflatex",
        description="LaTeX compiler to use (pdflatex, xelatex, lualatex)",
    )
    is_active: bool = Field(default=True, description="Whether this template is active")


class UserTemplateCreate(UserTemplateBase):
    pass


class UserTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    latex_content: Optional[str] = Field(None, min_length=1)
    compiler: Optional[str] = None
    is_active: Optional[bool] = None


class UserTemplate(UserTemplateBase):
    id: int
    user_id: int
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True
