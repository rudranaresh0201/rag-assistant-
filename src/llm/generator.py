from __future__ import annotations

import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

OLLAMA_MODEL = "phi3"
OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/generate"
MAX_CONTEXT_CHARS = 1500 
MAX_ANSWER_WORDS = 200
DEBUG_GENERATION = os.getenv("RAG_DEBUG_GENERATION", "0") == "1"
NO_ANSWER_TEXT = "I don't know"
MODEL_ERROR_TEXT = "Model error. Check Ollama."
MAX_SELECTED_CHUNKS = 1


def _truncate_context(context: str, max_chars: int = MAX_CONTEXT_CHARS) -> str:
    clean = context.strip()
    if len(clean) <= max_chars:
        return clean
    return clean[:max_chars].rsplit(" ", 1)[0].strip()


def _keyword_overlap(question: str, text: str) -> float:
    q_terms = set(re.findall(r"\b[a-z0-9]{3,}\b", question.lower()))
    if not q_terms:
        return 0.0
    t_terms = set(re.findall(r"\b[a-z0-9]{3,}\b", text.lower()))
    if not t_terms:
        return 0.0
    return len(q_terms & t_terms) / len(q_terms)


def _extract_clean_chunks(context: str) -> list[str]:
    blocks = [block.strip() for block in context.split("\n\n---\n\n") if block.strip()]
    cleaned_blocks: list[str] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        # Drop source header lines and keep only chunk text.
        lines = [line for line in lines if not line.startswith("[Source")]
        text = " ".join(lines).strip()
        if text:
            cleaned_blocks.append(text)

    return cleaned_blocks


def _select_top_chunks(question: str, context: str, max_chunks: int = MAX_SELECTED_CHUNKS) -> tuple[list[str], float]:
    cleaned_chunks = _extract_clean_chunks(context)
    if not cleaned_chunks:
        return [], 0.0

    ranked = sorted(
        cleaned_chunks,
        key=lambda chunk: _keyword_overlap(question, chunk),
        reverse=True,
    )
    selected = ranked[: max(1, max_chunks)]
    top_score = _keyword_overlap(question, selected[0]) if selected else 0.0
    return selected, top_score



def _build_prompt(question: str, clean_context: str) -> str:
    return f"""
Context:
{clean_context}

Question: {question}

Answer briefly in bullet points.
"""


def is_bad_output(response: str, question: str) -> bool:
    r = response.lower()
    if "according to" in r:
        return True
    if "the question" in r:
        return True
    if "the context" in r:
        return True
    if "question:" in r:
        return True
    if "answer:" in r:
        return True
    if question.lower() in r:
        return True

    too_short_markers = {"sure", "yes"}
    if r.strip() in too_short_markers:
        return True
    if not r.strip():
        return True

    if len(response.split()) > MAX_ANSWER_WORDS + 20:
        return True

    return False


def _trim_to_word_limit(text: str, max_words: int = MAX_ANSWER_WORDS) -> str:
    words = re.findall(r"\S+", text)
    if len(words) <= max_words:
        return text

    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    trimmed_lines: list[str] = []
    count = 0
    for line in lines:
        line_words = re.findall(r"\S+", line)
        if not line_words:
            continue
        if count + len(line_words) <= max_words:
            trimmed_lines.append(line)
            count += len(line_words)
            continue

        remaining = max_words - count
        if remaining > 0:
            partial = " ".join(line_words[:remaining]).rstrip(".,;:")
            if partial:
                trimmed_lines.append(partial + "...")
        break

    return "\n".join(trimmed_lines).strip()


def _clean_answer(answer: str, question: str) -> str:
    cleaned = answer.strip()

    # Remove QA labels and direct restatements before guard check.
    cleaned = re.sub(r"\bQuestion:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bAnswer:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(re.escape(question), "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = _trim_to_word_limit(cleaned, MAX_ANSWER_WORDS)

    if not cleaned:
        return NO_ANSWER_TEXT
    if is_bad_output(cleaned, question):
        return NO_ANSWER_TEXT
    return cleaned

def generate_answer(question: str, context: str) -> str | None:
    """Build a grounded RAG prompt and return model output or None on failure."""
    normalized_question = question.strip()
    normalized_context = _truncate_context(context)
    if not normalized_context:
        logger.warning("Empty context provided for generation")
        return NO_ANSWER_TEXT

    selected_chunks, top_score = _select_top_chunks(normalized_question, normalized_context)
    if not selected_chunks or top_score <= 0.0:
        logger.info("Weak or unrelated context detected (score=%.3f)", top_score)
        return NO_ANSWER_TEXT

    clean_context = "\n\n".join(selected_chunks)
    logger.info("Top chunks used: %s", [chunk[:160] for chunk in selected_chunks])
    prompt = _build_prompt(normalized_question, clean_context)

    try:
        logger.info("Using model: %s", OLLAMA_MODEL)
        print(f"Using model: {OLLAMA_MODEL}")
        print("Prompt length:", len(prompt))
        if DEBUG_GENERATION:
            logger.info("Question: %s", normalized_question)
            logger.info("Context preview: %s", clean_context[:1200])
            logger.info("Prompt preview: %s", prompt[:1200])

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "")

        if not isinstance(answer, str) or not answer.strip():
            print("Empty response")
            logger.warning("Ollama returned empty content")
            return NO_ANSWER_TEXT

        if DEBUG_GENERATION:
            logger.info("Model output preview: %s", answer[:1200])

        cleaned = _clean_answer(answer, normalized_question)
        if is_bad_output(cleaned, normalized_question):
            return NO_ANSWER_TEXT
        return cleaned
    except Exception as e:
        print("LLM ERROR:", e)
        logger.exception("Ollama generate failed: %s", e)
        return MODEL_ERROR_TEXT
