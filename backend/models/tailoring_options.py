from pydantic import BaseModel

from .ai_models import AIModel
from .templates import DEFAULT_TEMPLATE


class TailoringOptionsBase(BaseModel):
    ai_model: AIModel = AIModel.gpt_4_1_mini
    resume_template: str = DEFAULT_TEMPLATE
