"""OpenAI-compatible chat completions adapter, configured at runtime."""

import httpx

from app.core.errors import DependencyTimeout, DependencyUnavailable
from app.core.settings import Settings
from app.modules.answering.ports import ModelOutput


class APIModel:
    def __init__(self, settings: Settings):
        if settings.model_provider != "openai-compatible":
            raise ValueError("不支持的模型 Provider")
        if not all((settings.model_url, settings.model_name, settings.model_api_key)):
            raise ValueError("需要配置 IMM_AGENT_MODEL_URL、MODEL_NAME 和 MODEL_API_KEY")
        self.url = settings.model_url
        self.model_name = settings.model_name
        self.api_key = settings.model_api_key
        self.timeout = settings.model_timeout_seconds

    def complete(self, system: str, user: str) -> ModelOutput:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.url, headers={"Authorization": f"Bearer {self.api_key}"}, json={
                    "model": self.model_name, "temperature": 0,
                    "response_format": {"type": "json_object"},
                    "messages": [{"role": "system", "content": system},
                                 {"role": "user", "content": user}],
                })
                response.raise_for_status()
                body = response.json()
        except httpx.TimeoutException as exc:
            raise DependencyTimeout("模型服务超时") from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise DependencyUnavailable("模型服务不可用或响应格式无效") from exc
        try:
            content = body["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("empty content")
            usage = body.get("usage") or {}
            return ModelOutput(content=content, model=body.get("model") or self.model_name,
                               input_tokens=usage.get("prompt_tokens"),
                               output_tokens=usage.get("completion_tokens"))
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise DependencyUnavailable("模型服务响应格式无效") from exc
