"""Migrated public reads must remain usable after their transaction closes."""

import pytest
from pydantic import ValidationError
from sqlalchemy import inspect

from app.modules.knowledge.evidence import eligible_chunks
from app.modules.knowledge.models import Chunk
from app.modules.knowledge.schemas import ChunkSnapshot, DocumentSummary, VersionSnapshot
from app.modules.knowledge.service import change_status, get_document, latest_version, list_documents


def test_public_results_are_detached_and_read_only(session, source):
    doc, version = source
    chunk = Chunk(version_id=version.id, sequence=0, title_path='Heading', text=version.text,
                  char_start=0, char_end=len(version.text))
    session.add(chunk)
    session.commit()
    key, chunk_id = doc.id, chunk.id
    with session.begin():
        published = change_status(session, key, 'publish')
    summary = get_document(session, key)
    current = latest_version(session, key)
    chunks = eligible_chunks(session, [chunk_id, chunk_id])
    documents = list_documents(session)
    session.close()

    assert isinstance(published, DocumentSummary)
    assert isinstance(summary, DocumentSummary)
    assert isinstance(current, VersionSnapshot)
    assert len(chunks) == 1 and isinstance(chunks[0], ChunkSnapshot)
    assert chunks[0].text == current.text
    assert documents == [summary]
    for value in [published, summary, current, *chunks, *documents]:
        assert inspect(value, raiseerr=False) is None
    with pytest.raises(ValidationError):
        summary.status = 'withdrawn'


def test_status_and_index_job_roll_back_together(session, source):
    from sqlalchemy import select
    from app.modules.knowledge.models import IndexJob

    key = source[0].id
    change_status(session, key, 'publish')
    session.rollback()
    assert get_document(session, key).status == 'pending'
    assert list(session.scalars(select(IndexJob))) == []
