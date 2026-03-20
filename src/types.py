from __future__ import annotations

from typing import Any, TypedDict


class DocumentMetadata(TypedDict, total=False):
    source: str
    file_type: str
    file_path: str
    chunk_index: int
    total_chunks: int


class Document(TypedDict):
    content: str
    metadata: DocumentMetadata


class RetrievedChunk(TypedDict):
    content: str
    metadata: dict[str, Any]
    distance: float
    similarity: float
    relevance: float


class QAResponse(TypedDict):
    success: bool
    answer: str
    prompt: str
    sources: list[dict[str, Any]]
    relevance_score: float
    num_sources: int
    error: str | None
