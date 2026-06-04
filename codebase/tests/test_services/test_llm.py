from types import SimpleNamespace

from src.services.llm import LLMService


def test_llm_service_is_disabled_without_key():
    service = LLMService(api_key="", enabled=True)

    result = service.generate_chatbot_copy(
        mode="followup",
        user_message="hello",
        profile={},
    )

    assert result.used_provider is False
    assert result.error == "LLM is not configured."


def test_llm_service_calls_openai_responses(monkeypatch):
    calls = {}

    class FakeResponses:
        def create(self, **kwargs):
            calls.update(kwargs)
            return SimpleNamespace(output_text="Xin chào từ LLM.")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls["client_kwargs"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setitem(__import__("sys").modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    service = LLMService(api_key="test-key", model="test-model", enabled=True)

    result = service.generate_chatbot_copy(
        mode="recommendation",
        user_message="hello",
        profile={"destination": "Phu Quoc"},
        cards=[{"option": "A"}],
    )

    assert result.used_provider is True
    assert result.provider == "openai"
    assert result.text == "Xin chào từ LLM."
    assert calls["client_kwargs"]["api_key"] == "test-key"
    assert calls["model"] == "test-model"
