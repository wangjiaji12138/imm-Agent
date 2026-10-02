import json
from datetime import datetime
from pathlib import Path

from app.modules.evaluation.dataset import validate_evaluations
from app.modules.knowledge.text import content_hash
from app.modules.knowledge.models import Document, DocumentVersion

ROOT = Path(__file__).resolve().parents[2]
EVALS = ROOT / 'evals/questions.jsonl'
# Compose mounts evals at /app/evals rather than /evals.
if not EVALS.exists():
    EVALS = Path('/app/evals/questions.jsonl')


def seed_evidence(session):
    rows = [json.loads(line) for line in EVALS.read_text().splitlines()]
    source_ids = {key for row in rows for key in row['expected_source_ids']}
    for key in source_ids:
        doc = Document(id=key, title='Synthetic evidence fixture', organization='Test', source_url=f'https://example.org/{key}',
                       source_key=content_hash(key), language='en', fetched_at=datetime.utcnow(), status='published')
        session.add(doc)
        session.flush()
        session.add(DocumentVersion(document_id=key, text='Test evidence', content_hash=content_hash('Test evidence'), version_number=1))
    session.commit()
    return rows


def test_full_dataset_ready_only_when_sources_published(session):
    assert not validate_evaluations(EVALS, session)['ready']
    session.rollback()
    rows = seed_evidence(session)
    result = validate_evaluations(EVALS, session)
    assert result == dict(ready=True, total=20, dev=15, test=5, errors=[])
    source_id = rows[0]['expected_source_ids'][0]
    session.get(Document, source_id).status = 'withdrawn'
    session.commit()
    assert not validate_evaluations(EVALS, session)['ready']


def test_duplicates_missing_history_and_placeholder(session, tmp_path):
    rows = seed_evidence(session)
    rows[1]['id'] = rows[0]['id']
    del rows[12]['history']
    path = tmp_path / 'bad.jsonl'
    path.write_text('\n'.join(json.dumps(row) for row in rows) + '\nTODO_MISSING_SOURCE')
    result = validate_evaluations(path, session)
    assert not result['ready']
    assert any('ID' in error for error in result['errors'])
    assert any('history' in error for error in result['errors'])
    assert any('TODO_MISSING_SOURCE' in error for error in result['errors'])
