from datetime import datetime

from pydantic import BaseModel


class LegalAuthorizationBase(BaseModel):
    work_authorization: str


class LegalAuthorizationCreate(LegalAuthorizationBase):
    pass


class LegalAuthorization(LegalAuthorizationBase):
    id: int
    user_id: int
    last_updated: datetime

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models
