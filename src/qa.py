from __future__ import annotations

import logging

from src.retrieval.retriever import retrieve
from src.types import QAResponse, RetrievedChunk

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_N_RESULTS = 5
DEFAULT_DISTANCE_THRESHOLD = 0.7
MIN_QUESTION_LENGTH = 3
MAX_QUESTION_LENGTH = 500
MAX_CONTEXT_LENGTH = 4000  # Approximate token limit


def build_context(
	results: list[RetrievedChunk],
	max_length: int = MAX_CONTEXT_LENGTH,
) -> tuple[str, int]:
	"""
	Combine retrieved chunks into a single context string with token awareness.

	Args:
		results: List of retrieval results with 'content' key.
		max_length: Approximate character limit for context.

	Returns:
		Tuple of (context_string, num_chunks_used).
	"""
	context_parts: list[str] = []
	total_length = 0
	used_chunks = 0

	for idx, result in enumerate(results, start=1):
		content = result.get("content", "").strip()
		if not content:
			continue

		metadata = result.get("metadata", {})
		source = metadata.get("source", "unknown")
		chunk_index = metadata.get("chunk_index", "?")
		prefix = f"[Source {idx} | {source} | chunk {chunk_index}]\n"
		entry = f"{prefix}{content}"

		# Add separator before content (except first)
		if context_parts:
			separator = "\n\n---\n\n"
			total_length += len(separator)
		else:
			separator = ""

		# Check if adding this chunk would exceed limit
		if total_length + len(entry) > max_length:
			logger.debug(
				f"Context limit reached at {len(context_parts)} chunks "
				f"({total_length} chars)"
			)
			break

		if separator:
			context_parts.append(separator)
		context_parts.append(entry)
		total_length += len(entry)
		used_chunks += 1

	context = "".join(context_parts)
	logger.debug("Built context from %d chunks: %d chars", used_chunks, total_length)
	return context, used_chunks


def build_prompt(
	question: str,
	context: str,
	system_instruction: str | None = None,
) -> str:
	"""
	Construct a structured prompt for the LLM.

	Args:
		question: User's question.
		context: Retrieved context from documents.
		system_instruction: Optional custom system prompt.

	Returns:
		Formatted prompt string.
	"""
	if not system_instruction:
		system_instruction = (
			"You are a retrieval-grounded assistant. Answer only using the provided "
			"context snippets. If the context is insufficient or ambiguous, explicitly "
			"say you do not have enough information. Cite sources in square brackets, "
			"for example [Source 1]. Do not invent citations or facts."
		)

	prompt = f"""{system_instruction}

Context from documents:
{context}

User Question:
{question}

Instructions:
1. Answer in concise bullet points.
2. Include citations like [Source 1] for factual claims.
3. If uncertain, state what is missing and stop."""

	return prompt


def answer_question(
	question: str,
	n_results: int = DEFAULT_N_RESULTS,
	distance_threshold: float = DEFAULT_DISTANCE_THRESHOLD,
	collection_name: str = "knowledge_base",
	system_instruction: str | None = None,
) -> QAResponse:
	"""
	Run the full RAG pipeline: question → retrieve → build context → format prompt.

	Args:
		question: User's question to answer.
		n_results: Number of documents to retrieve.
		distance_threshold: Maximum distance (lower = more similar) for results.
		collection_name: Target vector database collection.
		system_instruction: Optional custom system prompt for the LLM.

	Returns:
		Dictionary with keys:
			- "success": bool indicating if retrieval succeeded
			- "answer": str (empty until LLM processes it)
			- "prompt": str to send to LLM
			- "sources": list of metadata from retrieved documents
			- "relevance_score": float (0-1) indicating result quality
			- "num_sources": int number of sources used
			- "error": str (if success=False)

	Raises:
		ValueError: If question is invalid.
	"""
	# Validate input
	if not question or not isinstance(question, str):
		raise ValueError("question must be a non-empty string.")

	question = question.strip()
	if len(question) < MIN_QUESTION_LENGTH:
		raise ValueError(
			f"question must be at least {MIN_QUESTION_LENGTH} characters."
		)
	if len(question) > MAX_QUESTION_LENGTH:
		raise ValueError(
			f"question must not exceed {MAX_QUESTION_LENGTH} characters."
		)

	logger.info(f"Processing question: {question[:60]}...")

	try:
		# 1. Retrieve relevant chunks
		logger.debug(f"Retrieving {n_results} results with threshold {distance_threshold}")
		results = retrieve(
			question,
			n_results=n_results,
			collection_name=collection_name,
			distance_threshold=distance_threshold,
		)

		if not results:
			logger.warning(f"No relevant documents found for: {question}")
			return {
				"success": False,
				"answer": "",
				"prompt": "",
				"sources": [],
				"relevance_score": 0.0,
				"num_sources": 0,
				"error": "No relevant documents found. Try a different query.",
			}

		# 2. Calculate average relevance score
		avg_relevance = sum(r.get("relevance", r.get("similarity", 0)) for r in results) / len(results)
		logger.debug("Average relevance score: %.3f", avg_relevance)

		# 3. Build context with token awareness
		context, num_chunks = build_context(results, max_length=MAX_CONTEXT_LENGTH)

		# 4. Build prompt for LLM
		prompt = build_prompt(question, context, system_instruction)

		# 5. Extract sorted sources
		sources = [
			{
				**r.get("metadata", {}),
				"similarity": r.get("similarity", 0),
				"relevance": r.get("relevance", r.get("similarity", 0)),
			}
			for r in results
		]

		logger.info(
			"Successfully built prompt from %d sources (avg relevance: %.3f, used chunks: %d)",
			len(results),
			avg_relevance,
			num_chunks,
		)

		return {
			"success": True,
			"answer": "",  # To be filled by LLM
			"prompt": prompt,
			"sources": sources,
			"relevance_score": avg_relevance,
			"num_sources": len(results),
			"error": None,
		}

	except ValueError as e:
		logger.error(f"Validation error: {e}")
		return {
			"success": False,
			"answer": "",
			"prompt": "",
			"sources": [],
			"relevance_score": 0.0,
			"num_sources": 0,
			"error": str(e),
		}
	except Exception as e:
		logger.error(f"Unexpected error in answer_question: {e}", exc_info=True)
		return {
			"success": False,
			"answer": "",
			"prompt": "",
			"sources": [],
			"relevance_score": 0.0,
			"num_sources": 0,
			"error": f"An unexpected error occurred: {str(e)}",
		}
