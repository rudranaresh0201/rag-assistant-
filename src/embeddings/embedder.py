from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

logger = logging.getLogger(__name__)


@lru_cache(maxsize=2)
def _get_model(model_name: str = DEFAULT_EMBEDDING_MODEL) -> SentenceTransformer:
    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name)


def embed_chunks(
    chunks: list[dict[str, Any]],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[list[float]]:
    if not chunks:
        return []

    texts = [chunk.get("content", "").strip() for chunk in chunks]
    if any(not text for text in texts):
        raise ValueError("All chunks must contain non-empty 'content'.")

    model = _get_model(model_name)
    embeddings = model.encode(texts)
    logger.info("Embedded %d chunks with model '%s'", len(texts), model_name)

    # SentenceTransformers may return ndarray-like structures.
    return [
        vector.tolist() if hasattr(vector, "tolist") else [float(v) for v in vector]
        for vector in embeddings
    ]
