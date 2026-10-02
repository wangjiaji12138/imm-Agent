"""Replaceable chat model boundary."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelOutput:
    content: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class ModelProvider(Protocol):
    def complete(self, system: str, user: str) -> ModelOutput: ...
