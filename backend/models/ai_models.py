from enum import Enum

class AIModel(str, Enum):
    """
    Enum for current OpenAI models
    """
    # GPT-4.1 models
    gpt_4_1_nano = "gpt-4.1-nano"
    
    # GPT-4o models
    gpt_4o = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
    
    # GPT-4 models
    gpt_4_turbo = "gpt-4-turbo"
    gpt_4 = "gpt-4"
    
    # O1 models
    gpt_o1 = "o1"
    gpt_o1_preview = "o1-preview"
    gpt_o1_mini = "o1-mini"
    
    # GPT-3.5 models
    gpt_3_5_turbo = "gpt-3.5-turbo"
