"""Qdrant HTTP adapter for the derived chunk index."""

import httpx

from app.core.errors import DependencyTimeout
from app.core.settings import Settings


class QdrantStore:
    def __init__(self, settings: Settings):
        self.base = f"{settings.qdrant_url.rstrip('/')}/collections/{settings.qdrant_collection}"
        self.client = httpx.Client(timeout=10.0)

    def ensure_collection(self, dimension: int, model_name: str) -> None:
        response = self.client.get(self.base)
        if response.status_code == 404:
            created = self.client.put(self.base, json={"vectors": {"size": dimension, "distance": "Cosine"}})
            created.raise_for_status()
            return
        response.raise_for_status()
        vectors = response.json()["result"]["config"]["params"]["vectors"]
        if vectors.get("size") != dimension:
            raise ValueError("Qdrant 集合维度与 Embedding 配置不一致，请使用新集合")

    def delete_document(self, document_id: str) -> None:
        response = self.client.post(f"{self.base}/points/delete", params={"wait": "true"}, json={
            "filter": {"must": [{"key": "document_id", "match": {"value": document_id}}]}})
        response.raise_for_status()

    def upsert(self, points: list[dict]) -> None:
        for start in range(0, len(points), 64):
            response = self.client.put(f"{self.base}/points", params={"wait": "true"},
                                       json={"points": points[start:start + 64]})
            response.raise_for_status()

    def query(self, vector: list[float], limit: int, offset: int = 0) -> list[dict]:
        try:
            response = self.client.post(f"{self.base}/points/query", json={
                "query": vector, "limit": limit, "offset": offset, "with_payload": True,
            })
        except httpx.TimeoutException as exc:
            raise DependencyTimeout("Qdrant 检索超时") from exc
        response.raise_for_status()
        return response.json()["result"]["points"]

    def close(self) -> None:
        self.client.close()
