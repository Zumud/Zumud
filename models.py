from enum import Enum

class AIModel(str, Enum):
    """
    Enum for current OpenAI models
    """
    # gpt_3_5_turbo_cheap = "gpt-3.5-turbo-0125"  # Since thse models do not support structured output, we have removed them
    # gpt_3_5_turbo = "gpt-3.5-turbo"
    gpt_4o = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
    # gpt_o1_preview = "o1-preview"  # Seems to be not working on the pypi
    # gpt_o1_mini = "o1-mini"
