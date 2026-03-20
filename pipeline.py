from __future__ import annotations

import copy
import logging
import importlib
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from functools import lru_cache
from typing import TypedDict

logger = logging.getLogger(__name__)

RETRIEVAL_TIMEOUT_SECONDS = 20
GENERATION_TIMEOUT_SECONDS = 120
MIN_SOURCE_SCORE = 0.10
MAX_INITIAL_CANDIDATES = 10
MAX_CACHE_ENTRIES = 256
MAX_CONTEXT_CHUNKS = 3
MAX_CONTEXT_CHARS = 3500
MAX_ANSWER_CHARS = 1200

_QUERY_CACHE: dict[tuple[str, int], "PipelineResult"] = {}


def _error_result(message: str) -> "PipelineResult":
    return {
        "answer": message,
        "sources": [],
        "confidence": 0.0,
        "latency": 0.0,
        "timings": {
            "retrieval": 0.0,
            "rerank": 0.0,
            "generation": 0.0,
        },
    }


def _run_with_timeout(func, *args, timeout: int, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=timeout)


@lru_cache(maxsize=1)
def _load_rag_functions():
    retriever_module = importlib.import_module("src.retrieval.retriever")
    generator_module = importlib.import_module("src.llm.generator")
    return retriever_module.retrieve, generator_module.generate_answer


def _cache_key(query: str, top_k: int) -> tuple[str, int]:
    return (query.lower().strip(), int(top_k))


def _get_cached_result(query: str, top_k: int) -> PipelineResult | None:
    key = _cache_key(query, top_k)
    cached = _QUERY_CACHE.get(key)
    if cached is None:
        return None
    return copy.deepcopy(cached)


def _set_cached_result(query: str, top_k: int, result: "PipelineResult") -> None:
    if len(_QUERY_CACHE) >= MAX_CACHE_ENTRIES:
        oldest_key = next(iter(_QUERY_CACHE))
        del _QUERY_CACHE[oldest_key]
    _QUERY_CACHE[_cache_key(query, top_k)] = copy.deepcopy(result)


class SourceItem(TypedDict):
    text: str
    score: float
    source: str


class PipelineResult(TypedDict):
    answer: str
    sources: list[SourceItem]
    confidence: float
    latency: float
    timings: dict[str, float]


def _build_context(retrieved: list[dict]) -> str:
    """Build source-tagged context for grounded generation."""
    blocks: list[str] = []
    for idx, item in enumerate(retrieved, start=1):
        text = str(item.get("content", "")).strip()
        if not text:
            continue

        metadata = item.get("metadata") or {}
        source = str(metadata.get("source", "unknown"))
        chunk_index = metadata.get("chunk_index", "?")
        blocks.append(f"[Source {idx} | {source} | chunk {chunk_index}]\n{text}")

    return "\n\n---\n\n".join(blocks)


def _truncate_context(text: str, max_chars: int = MAX_CONTEXT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].strip()


def _clean_context_chunks(chunks: list[SourceItem]) -> list[str]:
    cleaned: list[str] = []
    seen_signatures: set[str] = set()

    for chunk in chunks[:MAX_CONTEXT_CHUNKS]:
        text = str(chunk.get("text", "")).strip()
        if not text:
            continue

        # Remove repeated lines inside each chunk to reduce overlap noise.
        unique_lines: list[str] = []
        seen_lines: set[str] = set()
        for line in text.splitlines():
            normalized = " ".join(line.split()).strip().lower()
            if not normalized or normalized in seen_lines:
                continue
            seen_lines.add(normalized)
            unique_lines.append(line.strip())

        cleaned_text = "\n".join(unique_lines).strip()
        if not cleaned_text:
            continue

        signature = " ".join(cleaned_text.split()).lower()[:280]
        if signature in seen_signatures:
            continue

        seen_signatures.add(signature)
        cleaned.append(cleaned_text)

    return cleaned


def _post_process_answer(answer: str, max_chars: int = MAX_ANSWER_CHARS) -> str:
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    deduped_lines: list[str] = []
    seen: set[str] = set()
    for line in lines:
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped_lines.append(line)

    output = "\n".join(deduped_lines).strip()
    if len(output) <= max_chars:
        return output
    return output[:max_chars].rsplit(" ", 1)[0].strip()


def _normalize_scores(items: list[SourceItem]) -> list[SourceItem]:
    if not items:
        return []

    raw_scores = [max(0.0, float(i.get("score", 0.0) or 0.0)) for i in items]
    max_score = max(raw_scores)
    min_score = min(raw_scores)

    if max_score <= 0:
        for item in items:
            item["score"] = 0.0
        return items

    if max_score == min_score:
        for item in items:
            item["score"] = 1.0
        return items

    scale = max_score - min_score
    for item in items:
        normalized = (max(0.0, float(item.get("score", 0.0) or 0.0)) - min_score) / scale
        item["score"] = max(0.0, min(1.0, normalized))
    return items


def answer_query(query: str, top_k: int = 5) -> PipelineResult:
    """
    Main RAG entrypoint:
    query -> retrieve -> context build -> generate answer -> structured response.
    """
    start_total = time.time()
    retrieval_time = 0.0
    rerank_time = 0.0
    generation_time = 0.0
    try:
        if not isinstance(query, str) or not query.strip():
            return _error_result("Error occurred during processing")

        if not isinstance(top_k, int) or top_k <= 0:
            return _error_result("Error occurred during processing")

        normalized_query = query.strip()
        cached = _get_cached_result(normalized_query, top_k)
        if cached is not None:
            logger.info("[pipeline] cache hit | query=%s", normalized_query[:80])
            return cached

        print("[pipeline] start")
        logger.info("[pipeline] start | query=%s", normalized_query[:80])

        retrieve_fn, generate_answer_fn = _load_rag_functions()
        apply_rerank = len(normalized_query.split()) >= 4
        candidate_count = max(10, min(MAX_INITIAL_CANDIDATES, top_k * 2))

        print("[pipeline] retrieval")
        retrieval_start = time.time()
        retrieved = _run_with_timeout(
            retrieve_fn,
            query=normalized_query,
            n_results=candidate_count,
            apply_rerank=apply_rerank,
            timeout=RETRIEVAL_TIMEOUT_SECONDS,
        )
        retrieval_time = time.time() - retrieval_start
        print("[pipeline] retrieval done")
        logger.info("[pipeline] retrieval completed in %.2fs", retrieval_time)

        # RRF and rerank are performed inside retrieve().
        print("[pipeline] RRF")
        print("[pipeline] rerank")
        rerank_start = time.time()

        sources: list[SourceItem] = []
        for item in retrieved[:top_k]:
            metadata = item.get("metadata") or {}
            sources.append(
                {
                    "text": str(item.get("content", "")).strip(),
                    "score": float(item.get("relevance", item.get("similarity", 0.0)) or 0.0),
                    "source": str(metadata.get("source", "unknown")),
                }
            )

        sources = _normalize_scores(sources)
        filtered_sources = [s for s in sources if s["score"] >= MIN_SOURCE_SCORE]
        if filtered_sources:
            sources = filtered_sources

        top_chunks = sources[:MAX_CONTEXT_CHUNKS]
        if not top_chunks:
            top_chunks = [
                {
                    "text": str(item.get("content", "")).strip(),
                    "score": float(item.get("relevance", item.get("similarity", 0.0)) or 0.0),
                    "source": str((item.get("metadata") or {}).get("source", "unknown")),
                }
                for item in retrieved[:MAX_CONTEXT_CHUNKS]
                if str(item.get("content", "")).strip()
            ]

        cleaned_chunks = _clean_context_chunks(top_chunks)
        context = "\n\n".join(cleaned_chunks)
        context = _truncate_context(context)
        if not context.strip():
            logger.warning("Context build produced empty payload for query: %s", normalized_query[:80])
        rerank_time = 0.0 if not apply_rerank else (time.time() - rerank_start)
        print("[pipeline] rerank done")
        print("LLM start")
        generation_start = time.time()
        answer = _run_with_timeout(
            generate_answer_fn,
            question=normalized_query,
            context=context,
            timeout=GENERATION_TIMEOUT_SECONDS,
        )

        if not isinstance(answer, str) or not answer.strip():
            print("LLM error")
            summary = " ".join([chunk["text"][:150] for chunk in top_chunks[:2]])
            answer = "Answer based on retrieved documents:\n" + summary
        else:
            answer = _post_process_answer(answer)

        generation_time = time.time() - generation_start
        print("LLM success")
        logger.info("[pipeline] generation completed in %.2fs", generation_time)

        confidence = sum(s["score"] for s in sources) / len(sources) if sources else 0.0
        latency = time.time() - start_total
        response: PipelineResult = {
            "answer": answer,
            "sources": sources,
            "confidence": max(0.0, min(1.0, confidence)),
            "latency": float(latency),
            "timings": {
                "retrieval": float(retrieval_time),
                "rerank": float(rerank_time),
                "generation": float(generation_time),
            },
        }
        print("[pipeline] return")
        logger.info("[pipeline] return | total_time=%.2fs", latency)
        _set_cached_result(normalized_query, top_k, response)
        return response

    except FuturesTimeoutError:
        print("LLM error")
        logger.error("[pipeline] timeout after %.2fs", time.time() - start_total)
        return _error_result("Error occurred during processing")
    except Exception as exc:
        print("LLM error")
        logger.exception("[pipeline] failed after %.2fs: %s", time.time() - start_total, exc)
        return _error_result("Error occurred during processing")


try:
    _load_rag_functions()
    logger.info("[pipeline] warm load complete")
except Exception as exc:
    logger.warning("[pipeline] warm load failed: %s", exc)
