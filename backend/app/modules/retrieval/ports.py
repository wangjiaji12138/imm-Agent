"""Minimal external interfaces used by offline indexing."""

from typing import Protocol


class Embedding(Protocol):
    @property
    def dimension(self) -> int: ...

    @property
    def model_name(self) -> str: ...

    def encode(self, texts: list[str]) -> list[list[float]]: ...


class VectorStore(Protocol):
    def ensure_collection(self, dimension: int, model_name: str) -> None: ...

    def delete_document(self, document_id: str) -> None: ...

    def upsert(self, points: list[dict]) -> None: ...
