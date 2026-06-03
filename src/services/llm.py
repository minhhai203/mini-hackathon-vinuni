"""LLM service boundary.

Implement provider-specific logic here instead of wiring it directly into API
routes or agent nodes.
"""


class LLMService:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError("LLM provider is not configured yet.")
