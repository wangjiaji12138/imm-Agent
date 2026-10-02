"""Validate the real adapter's wire contract without calling a model service."""

import json

import httpx
import pytest

from app.core.settings import Settings
from app.infrastructure.embedding import APIEmbedding


def provider(monkeypatch, handler):
    client = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client(
        transport=httpx.MockTransport(handler), **kwargs))
    return APIEmbedding(Settings(_env_file=None, embedding_url="https://embedding.example/embeddings",
                                 embedding_model="test-model", embedding_api_key="test-key",
                                 embedding_dimension=2, embedding_batch_size=10))


def test_batches_request_dimensions_and_restore_input_order(monkeypatch):
    batch_sizes = []

    def handler(request):
        body = json.loads(request.content)
        batch_sizes.append(len(body["input"]))
        assert body["dimensions"] == 2
        assert body["encoding_format"] == "float"
        return httpx.Response(200, json={"data": [
            {"index": index, "embedding": [float(text), 1.0]}
            for index, text in reversed(list(enumerate(body["input"])))]})

    embeddings = provider(monkeypatch, handler).encode([str(i) for i in range(23)])
    assert batch_sizes == [10, 10, 3]
    assert embeddings == [[float(i), 1.0] for i in range(23)]


@pytest.mark.parametrize("data", [
    [{"index": 0, "embedding": [1, 2]}, {"index": 0, "embedding": [3, 4]}],
    [{"index": 0, "embedding": [1]}],
    [{"index": 0, "embedding": [True, 2]}],
    [{"embedding": [1, 2]}],
])
def test_malformed_embeddings_fail_closed(monkeypatch, data):
    embedding = provider(monkeypatch, lambda _: httpx.Response(200, json={"data": data}))
    with pytest.raises(ValueError, match="Embedding"):
        embedding.encode(["test"])
