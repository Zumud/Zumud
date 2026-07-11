from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .ai_models import AIModel
from .templates import ResumeTemplate


class TailoringOptionsBase(BaseModel):
    ai_model: AIModel = AIModel.gpt_4_1_mini
    resume_template: ResumeTemplate = ResumeTemplate.MTeck_resume


class TailoringOptionsCreate(TailoringOptionsBase):
    pass


class TailoringOptions(TailoringOptionsBase):
    id: Optional[int] = None
    user_id: Optional[int] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allows the Pydantic model to read data from ORM models
