from enum import Enum

class AIModel(str, Enum):
    """
    Enum for current OpenAI models
    """
    gpt_4o_mini = "gpt-4o-mini"
    gpt_4o = "gpt-4o"
    gpt_o1_mini = "o1-mini"
    gpt_o1_preview = "o1-preview"
    gpt_o1 = "o1"
