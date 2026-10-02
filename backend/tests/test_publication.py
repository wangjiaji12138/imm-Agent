import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.knowledge.schemas import ImportRecord
from app.modules.knowledge.service import change_status, import_record, latest_version, published_documents
from app.modules.knowledge.evidence import eligible_chunks
from app.modules.knowledge.models import Chunk, Document, IndexJob


def add_chunk(session, version):
    chunk = Chunk(version_id=version.id, sequence=0, title_path='Heading', text=version.text,
                  char_start=0, char_end=len(version.text))
    session.add(chunk)
    session.commit()
    return chunk.id


def test_pending_publish_withdraw_ignores_stale_index(session, source):
    doc, version = source
    chunk_id = add_chunk(session, version)
    assert eligible_chunks(session, [chunk_id]) == []
    assert published_documents(session) == []
    session.rollback()
    with session.begin():
        change_status(session, doc.id, 'publish')
    assert [c.id for c in eligible_chunks(session, [chunk_id])] == [chunk_id]
    session.rollback()
    with session.begin():
        change_status(session, doc.id, 'withdraw')
    # Simulate Qdrant returning the old point before deletion worker has run.
    assert eligible_chunks(session, [chunk_id]) == []
    jobs = list(session.scalars(select(IndexJob).where(IndexJob.action == 'delete')))
    assert len(jobs) == 1 and jobs[0].status == 'pending'


def test_expire_republish_and_illegal_transitions(session, source):
    doc, _ = source
    with pytest.raises(ValueError, match='不允许'):
        change_status(session, doc.id, 'expire')
    session.rollback()
    for action in ('publish', 'expire', 'publish'):
        with session.begin():
            change_status(session, doc.id, action)
    with pytest.raises(ValueError, match='不允许'):
        change_status(session, doc.id, 'publish')
    session.rollback()
    assert len(list(session.scalars(select(IndexJob)))) == 3


@pytest.mark.parametrize('field', ['title', 'organization', 'source_url', 'text', 'content_hash'])
def test_publish_requires_metadata_and_integrity(session, source, field):
    doc, version = source
    setattr(version if field in ('text', 'content_hash') else doc, field, '')
    session.commit()
    with pytest.raises(ValueError):
        change_status(session, doc.id, 'publish')
    session.rollback()
    assert session.get(Document, doc.id).status == 'pending'
    assert not list(session.scalars(select(IndexJob)))


def test_tampered_hash_is_rejected(session, source):
    doc, version = source
    version.content_hash = '0' * 64
    session.commit()
    with pytest.raises(ValueError, match='哈希'):
        change_status(session, doc.id, 'publish')


def test_new_version_requires_review_and_old_chunks_never_return(session, source, tmp_path):
    doc, version = source
    old_chunk = add_chunk(session, version)
    with session.begin():
        change_status(session, doc.id, 'publish')
    (tmp_path / 'new.txt').write_text('New test text.', encoding='utf-8')
    record = ImportRecord(title=doc.title, organization=doc.organization, source_url=doc.source_url,
                          language='en', text_path='new.txt')
    with session.begin():
        assert import_record(session, record, tmp_path)[0] == 'success'
    assert eligible_chunks(session, [old_chunk]) == []
    new_version = latest_version(session, doc.id)
    assert new_version.version_number == 2
    new_chunk = add_chunk(session, new_version)
    with session.begin():
        change_status(session, doc.id, 'publish')
    assert [c.id for c in eligible_chunks(session, [old_chunk, new_chunk, new_chunk])] == [new_chunk]


def test_gate_refreshes_loaded_sql_objects(engine, session, source):
    doc, version = source
    chunk_id = add_chunk(session, version)
    with session.begin():
        change_status(session, doc.id, 'publish')
    assert published_documents(session)[0].status == 'published'
    session.commit()
    with Session(engine) as admin, admin.begin():
        change_status(admin, doc.id, 'withdraw')
    assert eligible_chunks(session, [chunk_id]) == []
    assert published_documents(session) == []
