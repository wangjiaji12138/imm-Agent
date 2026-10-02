"""Model adapter wire contract without external calls."""

import json

import httpx
import pytest

from app.core.errors import DependencyTimeout
from app.core.settings import Settings
from app.infrastructure.llm import APIModel


def model(monkeypatch, handler):
    client = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client(
        transport=httpx.MockTransport(handler), **kwargs))
    return APIModel(Settings(_env_file=None, model_provider="openai-compatible",
                             model_url="https://model.example/chat/completions",
                             model_name="test-model", model_api_key="test-key"))


def test_chat_completion_json_contract(monkeypatch):
    def handler(request):
        body = json.loads(request.content)
        assert request.headers["Authorization"] == "Bearer test-key"
        assert body["model"] == "test-model" and body["temperature"] == 0
        assert body["response_format"] == {"type": "json_object"}
        assert body["messages"] == [{"role": "system", "content": "rules"},
                                    {"role": "user", "content": "question"}]
        return httpx.Response(200, json={"model": "test-model", "choices": [
            {"message": {"content": '{"result_type":"search","response":null}'}}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 7}})

    result = model(monkeypatch, handler).complete("rules", "question")
    assert (result.model, result.input_tokens, result.output_tokens) == ("test-model", 12, 7)


def test_model_timeout_is_dependency_error(monkeypatch):
    def handler(_):
        raise httpx.ReadTimeout("timed out")

    with pytest.raises(DependencyTimeout):
        model(monkeypatch, handler).complete("rules", "question")
