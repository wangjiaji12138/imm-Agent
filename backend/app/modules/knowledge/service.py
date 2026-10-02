"""文档导入+版本发布+检索证据过滤。

Caller-owned transactions keep publication and index jobs atomic. Public reads
return detached DTOs, never mapped objects or sessions.
"""

from datetime import timezone
from pathlib import Path
from sqlalchemy.orm import Session

from app.modules.knowledge import repository
from app.modules.knowledge.models import Document, DocumentVersion
from app.modules.knowledge.schemas import DocumentSummary, ImportRecord, VersionSnapshot
from app.modules.knowledge.text import canonical_url, clean_text, content_hash, document_id


def import_record(session: Session, record: ImportRecord, base_dir: Path) -> tuple[str, str]:
    """Caller owns one transaction per line. Existing document row serializes versions."""
    text = clean_text((base_dir / record.text_path).read_text(encoding="utf-8-sig"))
    if not text:
        raise ValueError("正文为空")
    url = canonical_url(record.source_url)
    digest = content_hash(text)
    key = content_hash(url)
    doc = repository.lock_source(session, key)
    if doc is not None:
        duplicate = repository.has_version_hash(session, doc.id, digest)
        if duplicate:
            return "skipped", doc.id
        previous = repository.latest_version(session, doc.id)
        number = previous.version_number + 1 if previous else 1
        if doc.status == "published" and previous:
            repository.add_index_job(session, doc.id, previous.id, "delete")
    else:
        doc = Document(id=document_id(url), source_url=url, source_key=key)
        session.add(doc)
        number = 1
    doc.title = record.title
    doc.organization = record.organization
    doc.language = record.language
    doc.published_at = record.published_at
    doc.fetched_at = record.fetched_at.astimezone(timezone.utc).replace(tzinfo=None)
    doc.status = "pending"
    session.flush()
    session.add(DocumentVersion(document_id=doc.id, text=text, content_hash=digest, version_number=number))
    session.flush()
    return "success", doc.id


TRANSITIONS = {
    "publish": ({"pending", "expired", "withdrawn"}, "published", "upsert"),
    "withdraw": ({"pending", "published", "expired"}, "withdrawn", "delete"),
    "expire": ({"published"}, "expired", "delete"),
}


def change_status(session: Session, source_id: str, action: str) -> DocumentSummary:
    doc = repository.lock_document(session, source_id)
    if doc is None:
        raise ValueError("资料不存在")
    allowed, target, job_action = TRANSITIONS[action]
    if doc.status not in allowed:
        raise ValueError(f"不允许从 {doc.status} 执行 {action}")
    version = repository.latest_version(session, doc.id)
    if version is None:
        raise ValueError("资料缺少正文版本")
    if action == "publish":
        if not all(value and value.strip() for value in (doc.title, doc.organization, doc.source_url, version.text, version.content_hash)):
            raise ValueError("发布需要标题、机构、来源 URL、正文和内容哈希")
        canonical_url(doc.source_url)
        if content_hash(version.text) != version.content_hash:
            raise ValueError("正文内容哈希不匹配")
    doc.status = target
    repository.add_index_job(session, doc.id, version.id, job_action)
    session.flush()
    return DocumentSummary.model_validate(doc)


def get_document(session: Session, source_id: str) -> DocumentSummary | None:
    doc = repository.get_document(session, source_id)
    return DocumentSummary.model_validate(doc) if doc is not None else None


def list_documents(session: Session) -> list[DocumentSummary]:
    return [DocumentSummary.model_validate(doc) for doc in repository.list_documents(session)]


def latest_version(session: Session, source_id: str) -> VersionSnapshot | None:
    version = repository.latest_version(session, source_id)
    return VersionSnapshot.model_validate(version) if version is not None else None


def published_documents(session: Session) -> list[DocumentSummary]:
    return [DocumentSummary.model_validate(doc) for doc in repository.published_documents(session)]


def source_readiness_error(session: Session, source_id: str) -> str | None:
    """Resolve an evaluation source without exposing knowledge table internals."""
    doc = get_document(session, source_id)
    if doc is None:
        return f'{source_id}: TODO_MISSING_SOURCE，数据库不存在此资料'
    if doc.status != 'published':
        return f'{source_id}: 资料未发布（{doc.status}）'
    version = latest_version(session, source_id)
    if version is None or not version.text.strip() or content_hash(version.text) != version.content_hash:
        return f'{source_id}: 正文缺失或哈希无效'
    return None
