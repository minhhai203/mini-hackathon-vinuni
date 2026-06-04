"""Chat API schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    profile: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    profile: dict[str, Any]
    suggestions: list[str] = Field(default_factory=list)
    cards: list[dict[str, Any]] = Field(default_factory=list)
    confidence: str
    needs_followup: bool = False
    used_tools: list[str] = Field(default_factory=list)
    safety_notice: str | None = None
    ui_theme: str = "theme-default"
    context: dict[str, Any] = Field(default_factory=dict)
    data_source: str | None = None
