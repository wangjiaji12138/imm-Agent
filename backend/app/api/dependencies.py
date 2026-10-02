"""Lazy composition of readiness, chat and source database dependencies."""

from dataclasses import dataclass
from collections.abc import Callable, Iterator

from sqlalchemy.orm import Session

from app.core.errors import DependencyUnavailable
from app.core.settings import get_settings
from app.infrastructure.database import get_session
from app.infrastructure.embedding import APIEmbedding
from app.infrastructure.llm import APIModel
from app.infrastructure.readiness import mysql_is_ready, qdrant_is_ready
from app.infrastructure.vector_store import QdrantStore
from app.modules.retrieval.schemas import SearchResult
from app.modules.retrieval.service import search_knowledge


def check_mysql() -> bool:
    return mysql_is_ready(get_settings())


def check_qdrant() -> bool:
    return qdrant_is_ready(get_settings())


@dataclass(frozen=True)
class ChatRuntime:
    provider: object
    search: Callable[[str], list[SearchResult]]
    session_factory: Callable[[], Session] = get_session


def get_chat_runtime() -> ChatRuntime:
    """No external connection is opened for a routed non-search request."""
    settings = get_settings()
    try:
        provider = APIModel(settings)
    except ValueError as exc:
        raise DependencyUnavailable("模型配置无效") from exc

    def search(message: str) -> list[SearchResult]:
        try:
            embedding = APIEmbedding(settings)
        except ValueError as exc:
            raise DependencyUnavailable("Embedding 配置无效") from exc
        store = QdrantStore(settings)
        try:
            with get_session() as session:
                try:
                    return search_knowledge(message, limit=5, session=session, embedding=embedding, store=store)
                except ValueError as exc:
                    raise DependencyUnavailable("检索响应无效") from exc
        finally:
            store.close()

    return ChatRuntime(provider=provider, search=search)


def source_session() -> Iterator[Session]:
    with get_session() as session:
        yield session
