from dataclasses import dataclass
from .ai_models import AIModel
from .templates import ResumeTemplate

@dataclass
class TailoringOptions:
    ai_model: AIModel = AIModel.gpt_4o_mini  # This is the cheapest model we have whch supports structured output
    resume_template: ResumeTemplate = ResumeTemplate.MTeck_resume  # This is the most popular template we have
