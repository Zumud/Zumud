from enum import Enum

class AIModel(str, Enum):
    gpt_3_5_turbo_cheap = "gpt-3.5-turbo-0125"
    gpt_3_5_turbo = "gpt-3.5-turbo"
    gpt_4o = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
