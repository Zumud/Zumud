from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models


class UserPreferenceCreate(BaseModel):
    preference: str


class UserPreference(BaseModel):
    preferences_text: str
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models
