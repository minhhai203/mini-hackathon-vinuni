"""OpenAI-compatible provider — works for OpenAI and any local server (Ollama, LM Studio)."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from src.logger import get_logger
from src.providers.base import WEATHER_TOOL_SCHEMA, LLMProvider, build_system_prompt, execute_tool

log = get_logger("chatbot.provider.openai")

# OpenAI tool format wraps the schema under a "function" key
_OPENAI_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": WEATHER_TOOL_SCHEMA,
    }
]


class OpenAICompatibleProvider(LLMProvider):
    """
    Provider for OpenAI models **and** any OpenAI-compatible local server.

    For OpenAI (cloud):
        Required env vars: OPENAI_API_KEY, OPENAI_MODEL
        base_url: leave as None (uses api.openai.com)

    For local servers (Ollama, LM Studio, vLLM, …):
        Required env vars: LOCAL_LLM_BASE_URL, LOCAL_LLM_MODEL
        LOCAL_LLM_API_KEY is optional (defaults to "no-key")
        base_url: e.g. "http://localhost:11434/v1"  (Ollama)
                       "http://localhost:1234/v1"   (LM Studio)

    Note: local models must support tool/function calling.
    Models known to work: llama3.1, mistral-nemo, qwen2.5, phi3.5.
    """

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self._model = model
        self._client = OpenAI(
            api_key=api_key or "no-key",
            base_url=base_url,          # None → uses the default OpenAI endpoint
        )

    def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> tuple[str, list[str], dict[str, Any]]:
        messages = _build_messages(message, history or [])
        used_tools: list[str] = []
        context: dict[str, Any] = {}

        for _ in range(5):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    tools=_OPENAI_TOOLS,
                )
            except Exception as exc:
                log.error("OPENAI_ERROR | model=%s | error=%s", self._model, exc)
                raise

            choice = response.choices[0]

            if choice.finish_reason != "tool_calls":
                return choice.message.content or "", used_tools, context

            messages.append(choice.message)

            for tc in choice.message.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                log.debug("TOOL_CALL | name=%s | args=%s", fn_name, fn_args)
                used_tools.append(fn_name)
                result = execute_tool(fn_name, fn_args)
                if "error" in result:
                    log.warning("TOOL_ERROR | name=%s | result=%s", fn_name, result)
                else:
                    log.debug("TOOL_OK   | name=%s | result_keys=%s", fn_name, list(result.keys()))
                context[fn_name] = result
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

        return "", used_tools, context


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_messages(message: str, history: list[dict[str, str]]) -> list[dict]:
    msgs: list[dict] = [{"role": "system", "content": build_system_prompt()}]
    for turn in history:
        role = turn.get("role", "user")
        msgs.append({"role": role if role in {"user", "assistant"} else "user", "content": turn.get("content", "")})
    msgs.append({"role": "user", "content": message})
    return msgs
