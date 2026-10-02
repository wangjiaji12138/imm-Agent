from datetime import datetime

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.modules.knowledge.text import content_hash
from app.infrastructure.orm import Base
from app.modules.knowledge.models import Document, DocumentVersion


@pytest.fixture
def engine():
    engine = create_engine('sqlite://')

    @event.listens_for(engine, 'connect')
    def foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')

    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
def source(session):
    doc = Document(title='Synthetic test source', organization='Test', source_url='https://example.org/a',
                   source_key=content_hash('https://example.org/a'), language='en', fetched_at=datetime.utcnow())
    session.add(doc)
    session.flush()
    version = DocumentVersion(document_id=doc.id, text='Synthetic paragraph.',
                              content_hash=content_hash('Synthetic paragraph.'), version_number=1)
    session.add(version)
    session.commit()
    return doc, version
