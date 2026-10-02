"""Stable text normalization, content hashes and source identifiers."""

import hashlib
import re
from uuid import NAMESPACE_URL, uuid5

from pydantic import HttpUrl

### 文本清洗+哈希
def clean_text(text: str) -> str:
    """Preserve paragraph/title boundaries and Unicode character offsets."""
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_url(url: str | HttpUrl) -> str:
    parsed = HttpUrl(url)
    if parsed.username or parsed.password:
        raise ValueError("source_url cannot contain credentials")
    return str(parsed).split("#", 1)[0]


def document_id(url: str | HttpUrl) -> str:
    return str(uuid5(NAMESPACE_URL, canonical_url(url)))
