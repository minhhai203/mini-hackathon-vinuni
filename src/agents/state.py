"""Agent state schema."""

from typing import TypedDict


class AgentState(TypedDict, total=False):
    user_input: str
    answer: str
