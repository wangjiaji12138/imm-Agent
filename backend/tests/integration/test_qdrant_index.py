"""Opt-in real Qdrant check; isolated collection is removed after the test."""

import os
from uuid import uuid4

import pytest

from app.core.settings import Settings
from app.infrastructure.vector_store import QdrantStore

pytestmark = pytest.mark.skipif(os.environ.get("IMM_AGENT_TEST_QDRANT") != "1", reason="requires Qdrant")


def test_qdrant_upsert_replace_and_delete():
    settings = Settings(qdrant_collection=f"imm_agent_test_{uuid4().hex}")
    store = QdrantStore(settings)
    point_id = str(uuid4())
    document_id = str(uuid4())
    try:
        store.ensure_collection(2, "test-fixed")
        point = {"id": point_id, "vector": [1.0, 0.0], "payload": {
            "chunk_id": point_id, "document_id": document_id, "version_id": str(uuid4()),
            "title_path": "Test", "char_start": 0, "char_end": 4, "status": "published"}}
        store.upsert([point, point])
        response = store.client.post(f"{store.base}/points/scroll", json={"limit": 10, "with_payload": True})
        response.raise_for_status()
        assert response.json()["result"]["points"][0]["payload"] == point["payload"]
        assert len(response.json()["result"]["points"]) == 1
        store.delete_document(document_id)
        response = store.client.post(f"{store.base}/points/scroll", json={"limit": 10})
        response.raise_for_status()
        assert response.json()["result"]["points"] == []
    finally:
        store.client.delete(store.base).raise_for_status()
        store.close()
