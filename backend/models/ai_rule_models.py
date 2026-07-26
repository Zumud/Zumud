from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_AI_RULE_INSTRUCTION_LENGTH = 500
MAX_AI_RULE_TITLE_LENGTH = 120


def _clean_text(value: str) -> str:
    return value.replace("\x00", "").strip()


class UserAIRuleCreate(BaseModel):
    title: str | None = Field(default=None, max_length=MAX_AI_RULE_TITLE_LENGTH)
    instruction: str = Field(..., max_length=MAX_AI_RULE_INSTRUCTION_LENGTH)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = _clean_text(value)
        return cleaned or None

    @field_validator("instruction")
    @classmethod
    def clean_instruction(cls, value: str) -> str:
        cleaned = _clean_text(value)
        if not cleaned:
            raise ValueError("Instruction cannot be empty.")
        return cleaned


class UserAIRuleUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=MAX_AI_RULE_TITLE_LENGTH)
    instruction: str | None = Field(
        default=None, max_length=MAX_AI_RULE_INSTRUCTION_LENGTH
    )
    is_enabled: bool | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = _clean_text(value)
        return cleaned or None

    @field_validator("instruction")
    @classmethod
    def clean_instruction(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = _clean_text(value)
        if not cleaned:
            raise ValueError("Instruction cannot be empty.")
        return cleaned


class UserAIRule(BaseModel):
    id: int
    title: str | None
    instruction: str
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
