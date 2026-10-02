from dataclasses import dataclass, field

import pytest
from sqlalchemy import select

from app.modules.knowledge.models import Chunk, DocumentVersion, IndexJob
from app.modules.knowledge.service import change_status, fail_index_jobs
from app.modules.knowledge.text import content_hash
from app.modules.retrieval.chunking import MAX_CHARS, split_text
from app.modules.retrieval.indexing import reindex_document


class FakeEmbedding:
    dimension = 2
    model_name = "test-fixed"

    def encode(self, texts):
        return [[float(len(text)), 1.0] for text in texts]


@dataclass
class FakeStore:
    points: dict = field(default_factory=dict)

    def ensure_collection(self, dimension, model_name):
        assert (dimension, model_name) == (2, "test-fixed")

    def delete_document(self, document_id):
        self.points = {key: point for key, point in self.points.items()
                       if point["payload"]["document_id"] != document_id}

    def upsert(self, points):
        self.points.update({point["id"]: point for point in points})


def test_unicode_positions_and_sentence_split():
    text = "# 标题\n\n" + "癌症免疫疗法。" * 200
    chunks = split_text(text)
    assert len(chunks) > 1
    assert all(len(chunk.text) <= MAX_CHARS for chunk in chunks)
    assert all(text[chunk.char_start:chunk.char_end] == chunk.text for chunk in chunks)
    assert all(chunk.title_path == "标题" for chunk in chunks)
    assert all(chunk.text.endswith("。") for chunk in chunks)


def test_nested_and_sibling_headings_preserve_path():
    chunks = split_text("# 疗法\n## 机制\n第一段。\n## 限制\n第二段。\n# 来源\n第三段。")
    assert [chunk.title_path for chunk in chunks] == ["疗法 / 机制", "疗法 / 限制", "来源"]


def test_reindex_is_idempotent_and_removes_old_versions(session, source):
    doc, version = source
    store = FakeStore()
    with session.begin():
        change_status(session, doc.id, "publish")
    with session.begin():
        assert reindex_document(session, doc.id, FakeEmbedding(), store) == 1
    first = dict(store.points)
    with session.begin():
        assert reindex_document(session, doc.id, FakeEmbedding(), store) == 1
    assert store.points == first
    chunk = session.scalar(select(Chunk).where(Chunk.version_id == version.id))
    assert version.text[chunk.char_start:chunk.char_end] == chunk.text
    assert session.scalar(select(IndexJob).where(IndexJob.document_id == doc.id)).status == "succeeded"
    session.rollback()

    with session.begin():
        doc.status = "pending"
        newer = DocumentVersion(document_id=doc.id, text="Updated text.",
                                content_hash=content_hash("Updated text."), version_number=2)
        session.add(newer)
    with session.begin():
        change_status(session, doc.id, "publish")
    with session.begin():
        assert reindex_document(session, doc.id, FakeEmbedding(), store) == 1
    assert set(store.points).isdisjoint(first)
    assert {point["payload"]["version_id"] for point in store.points.values()} == {newer.id}
    session.rollback()

    with session.begin():
        change_status(session, doc.id, "withdraw")
    with session.begin():
        assert reindex_document(session, doc.id, FakeEmbedding(), store) == 0
    assert store.points == {}


def test_failed_write_keeps_job_retryable(session, source):
    doc, _ = source
    with session.begin():
        change_status(session, doc.id, "publish")

    class FailingStore(FakeStore):
        def upsert(self, points):
            raise RuntimeError("write failed")

    with pytest.raises(RuntimeError, match="write failed"):
        with session.begin():
            reindex_document(session, doc.id, FakeEmbedding(), FailingStore())
    with session.begin():
        fail_index_jobs(session, doc.id, "write failed")
    job = session.scalar(select(IndexJob).where(IndexJob.document_id == doc.id))
    assert (job.status, job.attempts) == ("failed", 1)
    session.rollback()
    with session.begin():
        assert reindex_document(session, doc.id, FakeEmbedding(), FakeStore()) == 1
    assert (job.status, job.attempts) == ("succeeded", 2)
