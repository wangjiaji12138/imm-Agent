"""Opt-in checks against an already migrated MySQL; all fixture writes roll back."""

import os
from datetime import datetime
from uuid import uuid4

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.database import get_engine
from app.knowledge import change_status, content_hash, eligible_chunks
from app.models import Base, Chunk, Document, DocumentVersion, IndexJob

pytestmark = pytest.mark.skipif(os.environ.get('IMM_AGENT_TEST_MYSQL') != '1', reason='requires migrated MySQL')


def test_mysql_schema_constraints_and_stale_candidate_gate():
    engine = get_engine()
    with engine.connect() as connection:
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
    with Session(engine) as session:
        try:
            key = str(uuid4())
            doc = Document(title='Rollback-only test', organization='Test', source_url=f'https://example.org/{key}',
                           source_key=content_hash(key), language='en', fetched_at=datetime.utcnow())
            session.add(doc)
            session.flush()
            version = DocumentVersion(document_id=doc.id, text='Test text', content_hash=content_hash('Test text'), version_number=1)
            session.add(version)
            session.flush()
            chunk = Chunk(version_id=version.id, sequence=0, title_path='', text=version.text, char_start=0, char_end=9)
            session.add(chunk)
            session.flush()
            assert doc.published_at is None
            assert eligible_chunks(session, [chunk.id]) == []
            with pytest.raises(OperationalError) as violation, session.begin_nested():
                doc.status = 'illegal'
                session.flush()
            assert violation.value.orig.args[0] == 3819  # MySQL CHECK violation
            with pytest.raises(IntegrityError), session.begin_nested():
                session.add(DocumentVersion(document_id=doc.id, text=version.text, content_hash=version.content_hash, version_number=2))
                session.flush()
            change_status(session, doc.id, 'publish')
            assert len(eligible_chunks(session, [chunk.id])) == 1
            change_status(session, doc.id, 'withdraw')
            assert eligible_chunks(session, [chunk.id]) == []
            assert session.scalar(select(IndexJob).where(IndexJob.document_id == doc.id, IndexJob.action == 'delete')).status == 'pending'
        finally:
            session.rollback()
            engine.dispose()
