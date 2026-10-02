"""OpenAI-compatible embeddings endpoint, configured explicitly at runtime."""

import math

import httpx

from app.core.settings import Settings
from app.core.errors import DependencyTimeout


class APIEmbedding:
    def __init__(self, settings: Settings):
        if not all((settings.embedding_url, settings.embedding_model, settings.embedding_api_key)):
            raise ValueError("需要配置 IMM_AGENT_EMBEDDING_URL、MODEL 和 API_KEY")
        self.url = settings.embedding_url
        self.model_name = settings.embedding_model
        self.api_key = settings.embedding_api_key
        self.dimension = settings.embedding_dimension
        self.batch_size = settings.embedding_batch_size

    def encode(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = []
        with httpx.Client(timeout=30.0) as client:
            for start in range(0, len(texts), self.batch_size):
                batch = texts[start:start + self.batch_size]
                try:
                    response = client.post(self.url, headers={"Authorization": f"Bearer {self.api_key}"},
                                           json={"model": self.model_name, "input": batch,
                                                 "dimensions": self.dimension, "encoding_format": "float"})
                except httpx.TimeoutException as exc:
                    raise DependencyTimeout("Embedding 服务超时") from exc
                response.raise_for_status()
                try:
                    data = sorted(response.json()["data"], key=lambda item: item["index"])
                    if [item["index"] for item in data] != list(range(len(batch))):
                        raise ValueError("invalid indices")
                    embeddings = [item["embedding"] for item in data]
                    if any(len(vector) != self.dimension or
                           any(isinstance(value, bool) or not isinstance(value, (int, float)) or
                               not math.isfinite(value) for value in vector) for vector in embeddings):
                        raise ValueError("invalid vectors")
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError("Embedding 返回格式、序号或维度无效") from exc
                vectors.extend(embeddings)
        return vectors
