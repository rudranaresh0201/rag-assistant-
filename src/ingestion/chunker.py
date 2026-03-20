"""
src/ingestion/chunker.py
------------------------
Splits loaded documents into smaller, overlapping text chunks.

Why chunk at all?
    • LLMs have a limited context window (token budget).
    • Smaller chunks make retrieval more precise — you fetch only the
      relevant paragraph, not an entire 50-page PDF.
    • Overlap between chunks prevents information from being lost at
      the boundary between two adjacent chunks.

Example (chunk_size=10, overlap=3):
    Text:   "ABCDEFGHIJ KLMNOPQRST UVWXYZ"
    Chunk1: "ABCDEFGHIJ"   (starts at 0)
    Chunk2: "HIJKLMNOPQ"   (starts at 7  = 10 - 3)
    Chunk3: "PQRSTUVWXY"   (starts at 14 = 7  + 7)
    ...
"""

import logging

from src.config.settings import CHUNK_OVERLAP, CHUNK_SIZE
from src.types import Document

logger = logging.getLogger(__name__)


# ── Core splitting function ───────────────────────────────────────────────────

def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split a string into overlapping fixed-size character chunks.

    Args:
        text:       The document text to split.
        chunk_size: Maximum number of characters per chunk.
        overlap:    Characters of overlap between consecutive chunks.
                    Must be less than chunk_size.

    Returns:
        List of non-empty text chunks.
    """
    if not text or not text.strip():
        return []

    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be less than chunk_size ({chunk_size})."
        )

    chunks: list[str] = []
    step = chunk_size - overlap   # how far to advance the window each time
    start = 0

    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:                  # skip chunks that are all whitespace
            chunks.append(chunk)
        start += step

    return chunks


# ── Document-level chunker ────────────────────────────────────────────────────

def chunk_document(
    document: Document,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """
    Chunk a single document dict into multiple chunk dicts.

    Each chunk inherits the parent document's metadata so we always
    know *which file* a chunk came from (needed for citations).

    Args:
        document:   dict with 'content' (str) and 'metadata' (dict).
        chunk_size: chars per chunk.
        overlap:    chars of overlap.

    Returns:
        List of chunk dicts:
        {
            "content":  str,    ← the chunk text
            "metadata": {
                ...parent metadata...,
                "chunk_index":  int,   ← position of this chunk (0-based)
                "total_chunks": int,   ← total chunks from this document
            }
        }
    """
    raw_chunks = split_into_chunks(document["content"], chunk_size, overlap)
    total = len(raw_chunks)

    return [
        {
            "content": chunk_text,
            "metadata": {
                **document["metadata"],        # inherit source, file_type, …
                "chunk_index":  idx,
                "total_chunks": total,
            },
        }
        for idx, chunk_text in enumerate(raw_chunks)
    ]


# ── Batch chunker ─────────────────────────────────────────────────────────────

def chunk_documents(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """
    Chunk every document in *documents* and return a flat list.

    Args:
        documents:  List of document dicts from the loader.
        chunk_size: chars per chunk.
        overlap:    chars of overlap.

    Returns:
        Flat list of all chunk dicts from all documents.
    """
    all_chunks: list[Document] = []

    for doc in documents:
        chunks = chunk_document(doc, chunk_size, overlap)
        all_chunks.extend(chunks)
        logger.info(
            "Chunked '%s' into %d chunks",
            doc["metadata"].get("source", "unknown"),
            len(chunks),
        )

    logger.info("Total chunks produced: %d", len(all_chunks))
    return all_chunks
