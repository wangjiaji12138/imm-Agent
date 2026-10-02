"""Online vector retrieval with an SQL-authoritative evidence gate."""

from app.core.errors import DependencyTimeout

from app.modules.knowledge.evidence import search_evidence
from app.modules.retrieval.schemas import Candidate, SearchFilters, SearchInput, SearchResult


RetrievalTimeout = DependencyTimeout


def search_knowledge(query: str, filters: SearchFilters | dict | None = None, limit: int = 5,
                     *, session, embedding, store) -> list[SearchResult]:
    """Return up to limit current published chunks, in Qdrant score order.

    The caller owns the SQL session. Invalid input raises Pydantic ValidationError;
    dependency timeouts raise RetrievalTimeout, never an empty success result.
    """
    request = SearchInput.model_validate({"query": query, "filters": filters or {}, "limit": limit})
    vectors = embedding.encode([request.query])
    if len(vectors) != 1 or len(vectors[0]) != embedding.dimension:
        raise ValueError("查询 Embedding 数量或维度无效")
    results: list[SearchResult] = []
    offset = 0
    batch_size = max(50, request.limit * 5)
    seen: set[str] = set()
    while len(results) < request.limit:
        points = store.query(vectors[0], batch_size, offset)
        if not points:
            break
        offset += len(points)
        candidates = []
        for point in points:
            payload = point.get("payload") or {}
            chunk_id, version_id = payload.get("chunk_id"), payload.get("version_id")
            if isinstance(chunk_id, str) and isinstance(version_id, str) and chunk_id not in seen:
                seen.add(chunk_id)
                candidates.append(Candidate(chunk_id=chunk_id, version_id=version_id, score=point["score"]))
        verified = search_evidence(session, {item.chunk_id: item.version_id for item in candidates},
                                   language=request.filters.language,
                                   document_id=str(request.filters.document_id) if request.filters.document_id else None,
                                   published_from=request.filters.published_from,
                                   published_to=request.filters.published_to)
        results.extend(SearchResult(**verified[item.chunk_id].model_dump(), score=item.score)
                       for item in candidates if item.chunk_id in verified)
        if len(points) < batch_size:
            break
    return results[:request.limit]
