"""Reconcile one document's Qdrant points with its current SQL state."""

from app.modules.knowledge.service import finish_index_jobs, prepare_index
from app.modules.retrieval.chunking import split_text
from app.modules.retrieval.ports import Embedding, VectorStore


def reindex_document(session, source_id: str, embedding: Embedding, store: VectorStore) -> int:
    """Caller owns a transaction; row lock serializes publication and indexing."""
    snapshot = prepare_index(session, source_id, split_text)
    store.ensure_collection(embedding.dimension, embedding.model_name)
    if snapshot.version is not None:
        vectors = embedding.encode([chunk.text for chunk in snapshot.chunks])
        if len(vectors) != len(snapshot.chunks) or any(len(vector) != embedding.dimension for vector in vectors):
            raise ValueError("Embedding 返回数量或维度不匹配")
    else:
        vectors = []
    store.delete_document(source_id)
    if vectors:
        store.upsert([{"id": chunk.id, "vector": vector, "payload": {
            "chunk_id": chunk.id, "document_id": source_id, "version_id": snapshot.version.id,
            "title_path": chunk.title_path, "char_start": chunk.char_start,
            "char_end": chunk.char_end, "status": snapshot.document.status,
        }} for chunk, vector in zip(snapshot.chunks, vectors)])
    finish_index_jobs(session, source_id)
    return len(vectors)
