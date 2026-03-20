from __future__ import annotations

import hashlib
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection
from src.types import Document

logger = logging.getLogger(__name__)


def _to_list_embedding(embedding: Any) -> list[float]:
	"""Normalize an embedding to a plain Python list of floats."""
	if hasattr(embedding, "tolist"):
		embedding = embedding.tolist()

	if not isinstance(embedding, list):
		raise TypeError("Each embedding must be a list or array-like with tolist().")

	return [float(x) for x in embedding]


def _chunk_id(content: str) -> str:
	"""Build a stable ID so duplicates can be detected across runs."""
	return hashlib.sha256(content.encode("utf-8")).hexdigest()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "chroma.db"


@lru_cache(maxsize=1)
def _get_client() -> PersistentClient:
	DB_PATH.mkdir(parents=True, exist_ok=True)
	return PersistentClient(path=str(DB_PATH))


def get_collection(name: str = "knowledge_base") -> Collection:
	client = _get_client()
	return client.get_or_create_collection(name=name)

def store_chunks(
	chunks: Iterable[Document],
	embeddings: Iterable[Any],
	collection_name: str = "knowledge_base",
	batch_size: int = 128,
) -> int:
	"""
	Store chunk content + embedding + metadata in ChromaDB.

	Args:
		chunks: Iterable of dicts with keys: "content" (str), "metadata" (dict, optional).
		embeddings: Iterable of vector embeddings aligned with chunks.
		collection_name: Target Chroma collection name.
		batch_size: Number of records to write per request.

	Returns:
		Number of records successfully written.
	"""
	chunks_list = list(chunks)
	embeddings_list = list(embeddings)

	if len(chunks_list) != len(embeddings_list):
		raise ValueError(
			f"Length mismatch: chunks={len(chunks_list)} embeddings={len(embeddings_list)}"
		)
	if batch_size <= 0:
		raise ValueError("batch_size must be > 0")

	collection = get_collection(collection_name)
	logger.info(
		"Upserting %d chunks into collection '%s'",
		len(chunks_list),
		collection_name,
	)

	total_written = 0
	docs_batch: list[str] = []
	embs_batch: list[list[float]] = []
	metas_batch: list[dict[str, Any]] = []
	ids_batch: list[str] = []

	for chunk, embedding in zip(chunks_list, embeddings_list):
		content = chunk.get("content")
		if not isinstance(content, str) or not content.strip():
			raise ValueError("Every chunk must include non-empty string 'content'.")

		metadata = chunk.get("metadata") or {}
		if not isinstance(metadata, dict):
			raise ValueError("chunk['metadata'] must be a dict when provided.")

		docs_batch.append(content)
		embs_batch.append(_to_list_embedding(embedding))
		metas_batch.append(metadata)
		ids_batch.append(_chunk_id(content))

		if len(docs_batch) >= batch_size:
			collection.upsert(
				documents=docs_batch,
				embeddings=embs_batch,
				metadatas=metas_batch,
				ids=ids_batch,
			)
			total_written += len(docs_batch)
			docs_batch.clear()
			embs_batch.clear()
			metas_batch.clear()
			ids_batch.clear()

	if docs_batch:
		collection.upsert(
			documents=docs_batch,
			embeddings=embs_batch,
			metadatas=metas_batch,
			ids=ids_batch,
		)
		total_written += len(docs_batch)

	logger.info("Stored %d chunks in '%s'", total_written, collection_name)

	return total_written
