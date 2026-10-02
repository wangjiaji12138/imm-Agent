from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError

from app.infrastructure.orm import Base
from app.modules.knowledge.models import DocumentVersion


def test_status_constraint_and_unknown_date(session, source):
    doc, _ = source
    assert doc.published_at is None
    doc.status = 'approved'
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_version_hash_is_unique_per_document(session, source):
    doc, version = source
    session.add(DocumentVersion(document_id=doc.id, text=version.text,
                                content_hash=version.content_hash, version_number=2))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_migration_upgrade_repeat_downgrade():
    backend = Path(__file__).resolve().parents[1]
    config = Config(str(backend / 'alembic.ini'))
    engine = create_engine('sqlite://')
    with engine.begin() as connection:
        config.attributes['connection'] = connection
        command.upgrade(config, 'head')
        command.upgrade(config, 'head')
        assert set(Base.metadata.tables) <= set(inspect(connection).get_table_names())
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
        command.downgrade(config, 'base')
        assert not set(Base.metadata.tables) & set(inspect(connection).get_table_names())
