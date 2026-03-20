from __future__ import annotations

import logging

from src.config.logging_config import configure_logging
from src.ingestion.loader import load_all_documents
from src.ingestion.chunker import chunk_documents
from src.embeddings.embedder import embed_chunks
from src.vectorstore.store import store_chunks

logger = logging.getLogger(__name__)


def main() -> None:
	configure_logging()

	docs = load_all_documents()
	if not docs:
		logger.warning("No documents were loaded. Nothing to index.")
		return

	chunks = chunk_documents(docs)
	if not chunks:
		logger.warning("No chunks were generated. Nothing to index.")
		return

	embeddings = embed_chunks(chunks)
	stored = store_chunks(chunks, embeddings)
	logger.info("Indexing complete. Stored %d chunks.", stored)


if __name__ == "__main__":
	main()