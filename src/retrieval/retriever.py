from __future__ import annotations

import logging
import re
import time
from functools import lru_cache

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from src.config.settings import EMBEDDING_MODEL, TOP_K_RESULTS
from src.types import RetrievedChunk
from src.vectorstore.store import get_collection

logger = logging.getLogger(__name__)

# Module-level BM25 cache (function-based equivalent of self.documents / self.bm25).
_BM25_DOCS: dict[str, list[str]] = {}
_BM25_METAS: dict[str, dict[str, dict]] = {}
_BM25_INDEX: dict[str, BM25Okapi] = {}
_BM25_DOC_COUNT: dict[str, int] = {}

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
MAX_VECTOR_CANDIDATES = 10
MAX_BM25_CANDIDATES = 10
MAX_RERANK_CANDIDATES = 5

@lru_cache(maxsize=2)
def _get_embedding_model(model_name: str = EMBEDDING_MODEL) -> SentenceTransformer:
	"""
	Lazily load and cache the embedding model.

	Args:
		model_name: HuggingFace model identifier.

	Returns:
		Loaded SentenceTransformer model.
	"""
	logger.info("Loading embedding model: %s", model_name)
	return SentenceTransformer(model_name)


def _lexical_overlap_score(query: str, text: str) -> float:
	query_terms = set(re.findall(r"\w+", query.lower()))
	if not query_terms:
		return 0.0

	text_terms = set(re.findall(r"\w+", text.lower()))
	if not text_terms:
		return 0.0

	return len(query_terms & text_terms) / len(query_terms)


def _build_bm25_index(collection_name: str) -> None:
	"""Build or refresh BM25 index from vector-store documents."""
	collection = get_collection(collection_name)
	current_count = collection.count()

	if _BM25_DOC_COUNT.get(collection_name) == current_count and collection_name in _BM25_INDEX:
		return

	payload = collection.get(include=["documents", "metadatas"])
	raw_docs = payload.get("documents", []) or []
	raw_metas = payload.get("metadatas", []) or []

	documents: list[str] = []
	doc_to_meta: dict[str, dict] = {}
	for idx, raw_doc in enumerate(raw_docs):
		doc_text = (raw_doc or "").strip() if isinstance(raw_doc, str) else ""
		if not doc_text:
			continue
		documents.append(doc_text)
		meta = raw_metas[idx] if idx < len(raw_metas) and isinstance(raw_metas[idx], dict) else {}
		if doc_text not in doc_to_meta:
			doc_to_meta[doc_text] = meta

	if not documents:
		_BM25_DOCS[collection_name] = []
		_BM25_METAS[collection_name] = {}
		_BM25_DOC_COUNT[collection_name] = current_count
		if collection_name in _BM25_INDEX:
			del _BM25_INDEX[collection_name]
		return

	tokenized_docs = [doc.lower().split() for doc in documents]
	_BM25_INDEX[collection_name] = BM25Okapi(tokenized_docs)
	_BM25_DOCS[collection_name] = documents
	_BM25_METAS[collection_name] = doc_to_meta
	_BM25_DOC_COUNT[collection_name] = current_count


def rrf_score(rank: int, k: int = 60) -> float:
	return 1.0 / (k + rank)


def is_valid_chunk(text: str) -> bool:
	text_lower = text.lower()

	# Remove junk patterns
	if "table of contents" in text_lower:
		return False
	if "........" in text:
		return False
	if len(text.strip()) < 50:
		return False

	# Avoid mostly headings
	if text.count('.') > 10:
		return False

	return True


def retrieve(
	query: str,
	n_results: int = TOP_K_RESULTS,
	collection_name: str = "knowledge_base",
	model_name: str = EMBEDDING_MODEL,
	distance_threshold: float | None = None,
	apply_rerank: bool = True,
) -> list[RetrievedChunk]:
	"""
	Retrieve the most relevant document chunks for a query with scores.

	Args:
		query: Text query to search for.
		n_results: Maximum number of results to return.
		collection_name: Target Chroma collection name.
		model_name: HuggingFace embedding model to use.
		distance_threshold: Optional max distance filter (lower = more similar).

	Returns:
		List of dicts with keys: "content", "metadata", "distance".
		Sorted by distance (ascending, most similar first).

	Raises:
		ValueError: If query is empty or n_results <= 0.
		Exception: If retrieval fails.
	"""
	if not query or not isinstance(query, str):
		raise ValueError("query must be a non-empty string.")
	if n_results <= 0:
		raise ValueError("n_results must be > 0.")

	top_k = 3
	query_keywords = {word for word in query.lower().split() if word}
	blocked_phrases = ("table of contents", "page", "article", "chunk")

	try:
		# 1️⃣ Convert query to embedding
		model = _get_embedding_model(model_name)
		query_embedding = model.encode(query)
		logger.debug(f"Encoded query: {query[:50]}...")

		# 2️⃣ Get the vector database collection
		collection = get_collection(collection_name)
		logger.debug("Collection '%s' vector count: %d", collection_name, collection.count())
		_build_bm25_index(collection_name)

		# 3️⃣ Search for similar embeddings
		vector_n = max(top_k, min(MAX_VECTOR_CANDIDATES, max(10, n_results)))
		results = collection.query(
			query_embeddings=[query_embedding.tolist()],
			n_results=vector_n,
			include=["documents", "metadatas", "distances"],
		)

		# 4️⃣ Extract and structure retrieved documents
		documents = results.get("documents", [[]])[0]
		metadatas = results.get("metadatas", [[]])[0]
		distances = results.get("distances", [[]])[0]

		if not documents:
			logger.warning(f"No results found for query: {query}")
			return []

		# 5️⃣ Build result list with metadata and scores
		retrieved: list[RetrievedChunk] = []
		for doc, meta, dist in zip(documents, metadatas, distances):
			doc_text = (doc or "").strip()
			if not doc_text:
				continue

			doc_lower = doc_text.lower()
			if any(phrase in doc_lower for phrase in blocked_phrases):
				continue

			if query_keywords and not any(keyword in doc_lower for keyword in query_keywords):
				continue

			if distance_threshold is not None and dist > distance_threshold:
				continue

			similarity = 1.0 - float(dist)
			keyword_score = _lexical_overlap_score(query, doc)
			relevance = (0.85 * similarity) + (0.15 * keyword_score)

			retrieved.append(
				{
					"content": doc_text,
					"metadata": meta or {},
					"distance": float(dist),
					"similarity": similarity,
					"relevance": relevance,
				}
			)

		retrieved.sort(key=lambda item: item.get("relevance", 0.0), reverse=True)

		# Keep Chroma outputs as text list for hybrid merge.
		chroma_results = [item["content"] for item in retrieved]

		# BM25 keyword retrieval over full chunk corpus.
		bm25_results: list[str] = []
		bm25 = _BM25_INDEX.get(collection_name)
		documents = _BM25_DOCS.get(collection_name, [])
		if bm25 and documents:
			query_tokens = query.lower().split()
			bm25_scores = bm25.get_scores(query_tokens)
			bm25_top_indices = sorted(
				range(len(bm25_scores)),
				key=lambda i: bm25_scores[i],
				reverse=True,
			)[:MAX_BM25_CANDIDATES]
			for i in bm25_top_indices:
				candidate = documents[i]
				candidate_lower = candidate.lower()
				if any(phrase in candidate_lower for phrase in blocked_phrases):
					continue
				if query_keywords and not any(keyword in candidate_lower for keyword in query_keywords):
					continue
				bm25_results.append(candidate)

		# Strictly clean candidates before hybrid ranking.
		chroma_results = [doc for doc in chroma_results if is_valid_chunk(doc)]
		bm25_results = [doc for doc in bm25_results if is_valid_chunk(doc)]

		# Reciprocal Rank Fusion over Chroma and BM25 rankings.
		chroma_rank = {doc: rank + 1 for rank, doc in enumerate(chroma_results)}
		bm25_rank = {doc: rank + 1 for rank, doc in enumerate(bm25_results)}
		all_docs = set(chroma_results + bm25_results)

		scores: dict[str, float] = {}
		for doc in all_docs:
			score = 0.0
			if doc in chroma_rank:
				score += rrf_score(chroma_rank[doc])
			if doc in bm25_rank:
				score += rrf_score(bm25_rank[doc])
			scores[doc] = score

		ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

		# Cross-encoder reranking over top RRF candidates (optional for speed).
		use_rerank = apply_rerank and len(query.split()) >= 4
		if use_rerank:
			rerank_start = time.time()
			top_docs = [doc for doc, _ in ranked_docs[:MAX_RERANK_CANDIDATES]]
			pairs = [(query, doc) for doc in top_docs]
			rerank_scores = reranker.predict(pairs) if pairs else []
			doc_scores = list(zip(top_docs, rerank_scores))
			reranked = sorted(doc_scores, key=lambda x: x[1], reverse=True)
			final_texts = [doc for doc, _ in reranked[:top_k]]
			logger.info("Cross-encoder rerank enabled: %d candidates in %.2fs", len(top_docs), time.time() - rerank_start)
		else:
			final_texts = [doc for doc, _ in ranked_docs[:top_k]]
			logger.info("Cross-encoder rerank skipped for simple query")
		chroma_lookup = {item["content"]: item for item in retrieved}
		bm25_meta_lookup = _BM25_METAS.get(collection_name, {})
		final_results: list[RetrievedChunk] = []
		for text in final_texts:
			if text in chroma_lookup:
				final_results.append(chroma_lookup[text])
				continue

			similarity = _lexical_overlap_score(query, text)
			final_results.append(
				{
					"content": text,
					"metadata": bm25_meta_lookup.get(text, {}),
					"distance": 1.0 - similarity,
					"similarity": similarity,
					"relevance": similarity,
				}
			)

		logger.info("Retrieved %d chunks for query: %s...", len(final_results), query[:50])
		return final_results

	except Exception as e:
		logger.error(f"Retrieval failed for query '{query}': {e}", exc_info=True)
		raise
