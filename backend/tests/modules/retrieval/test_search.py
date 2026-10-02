"""Search contract and SQL evidence gate using deterministic local dependencies."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.core.errors import DependencyTimeout
from app.modules.knowledge.models import Chunk, DocumentVersion
from app.modules.knowledge.service import change_status
from app.modules.knowledge.text import content_hash
from app.modules.retrieval.service import RetrievalTimeout, search_knowledge


class Embedding:
    dimension = 2

    def encode(self, texts):
        return [[1.0, 0.0] for _ in texts]


class Store:
    def __init__(self, points):
        self.points = points

    def query(self, vector, limit, offset=0):
        assert vector == [1.0, 0.0]
        return self.points[offset:offset + limit]


def point(chunk, score=0.9, version_id=None):
    return {"payload": {"chunk_id": chunk.id, "version_id": version_id or chunk.version_id},
            "score": score}


def test_input_validation(session):
    for query, limit, filters in [(" ", 5, None), ("a", 5, None), ("x" * 501, 5, None),
                                  ("hello", 0, None), ("hello", 21, None),
                                  ("hello", 5, {"organization": "NCI"}),
                                  ("hello", 5, {"published_from": "2025-02-01", "published_to": "2025-01-01"})]:
        with pytest.raises(ValidationError):
            search_knowledge(query, filters, limit, session=session, embedding=Embedding(), store=Store([]))


def test_empty_and_published_filter(session, source):
    doc, version = source
    chunk = Chunk(version_id=version.id, sequence=0, title_path="", text=version.text,
                  char_start=0, char_end=len(version.text))
    session.add(chunk)
    session.commit()
    store = Store([point(chunk)])
    assert search_knowledge("sample", session=session, embedding=Embedding(), store=store) == []
    session.rollback()
    with session.begin():
        change_status(session, doc.id, "publish")
    doc.published_at = date(2024, 1, 15)
    session.commit()
    found = search_knowledge("sample", {"language": "en", "document_id": doc.id,
                                       "published_from": date(2024, 1, 1),
                                       "published_to": date(2024, 1, 31)},
                             session=session, embedding=Embedding(), store=store)
    assert len(found) == 1
    assert found[0].chunk_id == chunk.id and found[0].text == version.text
    assert found[0].title == doc.title and found[0].organization == doc.organization
    assert found[0].source_url == doc.source_url and found[0].published_at == doc.published_at
    assert search_knowledge("sample", {"language": "zh"}, session=session,
                            embedding=Embedding(), store=store) == []
    session.rollback()
    with session.begin():
        change_status(session, doc.id, "withdraw")
    assert search_knowledge("sample", session=session, embedding=Embedding(), store=store) == []


def test_old_version_and_forged_payload_are_rejected(session, source):
    doc, version = source
    old = Chunk(version_id=version.id, sequence=0, title_path="", text=version.text,
                char_start=0, char_end=len(version.text))
    session.add(old)
    newer = DocumentVersion(document_id=doc.id, text="New source text.",
                            content_hash=content_hash("New source text."), version_number=2)
    session.add(newer)
    session.flush()
    current = Chunk(version_id=newer.id, sequence=0, title_path="", text=newer.text,
                    char_start=0, char_end=len(newer.text))
    session.add(current)
    session.commit()
    with session.begin():
        change_status(session, doc.id, "publish")
    found = search_knowledge("sample", session=session, embedding=Embedding(),
                             store=Store([point(old), point(current, 0.8, version.id), point(current, 0.7)]))
    assert [item.chunk_id for item in found] == []  # forged first occurrence cannot be trusted
    found = search_knowledge("sample", session=session, embedding=Embedding(), store=Store([point(old), point(current)]))
    assert [item.chunk_id for item in found] == [current.id]


def test_qdrant_timeout_is_dependency_error(session):
    class TimeoutStore:
        def query(self, vector, limit, offset=0):
            raise DependencyTimeout("timed out")

    with pytest.raises(RetrievalTimeout):
        search_knowledge("sample", session=session, embedding=Embedding(), store=TimeoutStore())
