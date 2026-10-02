"""Qdrant query wire contract and timeout mapping."""

import json

import httpx
import pytest

from app.core.errors import DependencyTimeout
from app.core.settings import Settings
from app.infrastructure.vector_store import QdrantStore


def test_query_requests_payload_and_offset():
    store = QdrantStore(Settings(_env_file=None))

    def handler(request):
        assert request.url.path.endswith("/points/query")
        assert json.loads(request.content) == {"query": [1.0, 0.0], "limit": 5,
                                               "offset": 10, "with_payload": True}
        return httpx.Response(200, json={"result": {"points": [{"score": 0.8, "payload": {}}]}})

    store.client.close()
    store.client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        assert store.query([1.0, 0.0], 5, 10) == [{"score": 0.8, "payload": {}}]
    finally:
        store.close()


def test_query_timeout_is_dependency_error():
    store = QdrantStore(Settings(_env_file=None))

    def handler(_):
        raise httpx.ReadTimeout("timed out")

    store.client.close()
    store.client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(DependencyTimeout):
            store.query([1.0, 0.0], 5)
    finally:
        store.close()
