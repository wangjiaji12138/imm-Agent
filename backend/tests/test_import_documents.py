import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select

from app.cli.import_documents import import_manifest
from app.modules.knowledge.schemas import ImportRecord
from app.modules.knowledge.text import clean_text, document_id
from app.modules.knowledge.models import Document, DocumentVersion


def record(path='a.txt', url='https://example.org/a'):
    return dict(title='Test source', organization='Test', source_url=url, language='en',
                published_at=None, text_path=path)


def test_two_success_one_failure_then_two_skipped(session, tmp_path, capsys):
    (tmp_path / 'a.txt').write_text('  Synthetic  text.\n\n\nSecond paragraph. ', encoding='utf-8')
    manifest = tmp_path / 'manifest.jsonl'
    rows = [record(), record(url='https://example.org/b'), record('missing.txt')]
    manifest.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
    assert import_manifest(session, manifest, tmp_path) == dict(success=2, skipped=0, failed=1)
    assert import_manifest(session, manifest, tmp_path) == dict(success=0, skipped=2, failed=1)
    assert session.scalar(select(func.count()).select_from(Document)) == 2
    assert session.scalar(select(func.count()).select_from(DocumentVersion)) == 2
    doc = session.get(Document, document_id('https://example.org/a'))
    assert doc.published_at is None
    assert doc.status == 'pending'
    assert '"line": 3' in capsys.readouterr().out


@pytest.mark.parametrize('url', ['file:///etc/passwd', 'ftp://example.org', 'not-url', 'https://user:pass@example.org'])
def test_reject_invalid_urls(url):
    with pytest.raises(ValidationError):
        ImportRecord(**record(url=url))


@pytest.mark.parametrize('date', ['', 'unknown', '2025-02-30', 123, '2025-01-01T00:00:00'])
def test_reject_invalid_dates(date):
    with pytest.raises(ValidationError):
        ImportRecord(**(record() | {'published_at': date}))


def test_bad_json_and_empty_text_do_not_stop_later_lines(session, tmp_path):
    (tmp_path / 'a.txt').write_text('   ', encoding='utf-8')
    (tmp_path / 'b.txt').write_text('Valid test text.', encoding='utf-8')
    path = tmp_path / 'manifest.jsonl'
    path.write_text('{bad json\n' + json.dumps(record()) + '\n' + json.dumps(record('b.txt')))
    assert import_manifest(session, path, tmp_path) == dict(success=1, skipped=0, failed=2)


def test_cleaning_preserves_structure_and_stable_ids():
    assert clean_text(' 标题\r\n\r\n  A\t B\n\n\nC ') == '标题\n\nA B\n\nC'
    assert document_id('https://EXAMPLE.org/a#intro') == document_id('https://example.org/a')


def test_invalid_utf8_manifest_line_is_isolated(session, tmp_path):
    (tmp_path / 'a.txt').write_text('Valid text.', encoding='utf-8')
    path = tmp_path / 'manifest.jsonl'
    path.write_bytes(b'\xff\n' + json.dumps(record()).encode() + b'\n')
    assert import_manifest(session, path, tmp_path) == dict(success=1, skipped=0, failed=1)
