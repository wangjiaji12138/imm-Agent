"""Deterministic Unicode character spans for indexed source text."""

import re
from dataclasses import dataclass

MAX_CHARS = 1200


@dataclass(frozen=True)
class TextChunk:
    sequence: int
    title_path: str
    text: str
    char_start: int
    char_end: int


def _spans(text: str, start: int, end: int):
    """Split an oversized paragraph at sentence marks, then at a hard limit."""
    cursor = start
    while cursor < end:
        limit = min(cursor + MAX_CHARS, end)
        if limit < end:
            boundaries = [match.end() for match in re.finditer(r"[。！？；]|[.!?;](?:\s|$)", text[cursor:limit])]
            if boundaries:
                limit = cursor + boundaries[-1]
        yield cursor, limit
        cursor = limit


def split_text(text: str) -> list[TextChunk]:
    """Preserve exact offsets into the stored document version."""
    chunks: list[TextChunk] = []
    headings: list[tuple[int, str]] = []
    for match in re.finditer(r"[^\n]+(?:\n|$)", text):
        raw = match.group()
        line = raw.strip()
        heading = re.match(r"^(#{1,6})\s+(\S.*)", line)
        if heading:
            level = len(heading.group(1))
            headings = [(depth, title) for depth, title in headings if depth < level]
            headings.append((level, heading.group(2)))
            continue
        start = match.start() + len(raw) - len(raw.lstrip())
        end = match.end() - len(raw) + len(raw.rstrip())
        if start >= end:
            continue
        for left, right in _spans(text, start, end):
            piece = text[left:right]
            if piece.strip():
                chunks.append(TextChunk(len(chunks), " / ".join(title for _, title in headings), piece, left, right))
    return chunks
