"""Google Gemini provider via the google-genai SDK."""

from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types

from src.providers.base import SYSTEM_PROMPT, WEATHER_TOOL_SCHEMA, LLMProvider, execute_tool


def _build_gemini_tool() -> types.Tool:
    schema = WEATHER_TOOL_SCHEMA
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=schema["name"],
                description=schema["description"],
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        k: types.Schema(type=types.Type.STRING, description=v["description"])
                        for k, v in schema["parameters"]["properties"].items()
                    },
                    required=schema["parameters"]["required"],
                ),
            )
        ]
    )


class GoogleProvider(LLMProvider):
    """
    Gemini provider (gemini-2.5-flash-lite or any google-genai model).

    Required env vars:
        GOOGLE_API_KEY   — API key from Google AI Studio
        GEMINI_MODEL     — model ID, e.g. "gemini-2.5-flash-lite"
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._model = model
        self._client = genai.Client(api_key=api_key)
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[_build_gemini_tool()],
        )

    def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> tuple[str, list[str], dict[str, Any]]:
        gemini_history = [
            types.Content(
                role="user" if t.get("role") == "user" else "model",
                parts=[types.Part.from_text(text=t.get("content", ""))],
            )
            for t in (history or [])
        ]

        session = self._client.chats.create(
            model=self._model,
            config=self._config,
            history=gemini_history,
        )

        used_tools: list[str] = []
        context: dict[str, Any] = {}
        response = session.send_message(message)

        for _ in range(5):
            fn_calls = response.function_calls
            if not fn_calls:
                break

            parts: list[types.Part] = []
            for fc in fn_calls:
                used_tools.append(fc.name)
                result = execute_tool(fc.name, dict(fc.args))
                context[fc.name] = result
                parts.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response={"result": json.dumps(result, ensure_ascii=False)},
                    )
                )
            response = session.send_message(parts)

        return response.text or "", used_tools, context
