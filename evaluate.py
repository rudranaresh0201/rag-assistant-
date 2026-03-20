from __future__ import annotations

from pipeline import answer_query

from pipeline import answer_query

test_data = [
    {
        "question": "What is BAJA SAEINDIA?",
        "keywords": ["competition", "students", "vehicles"],
    },
    {
        "question": "What is a transponder?",
        "keywords": ["timing", "scoring"],
    },
    {
        "question": "What are the rules of BAJA?",
        "keywords": ["rules", "vehicle", "competition"],
    },
]


def compute_relevance(answer: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    answer_lower = answer.lower()
    matches = sum(1 for k in keywords if k.lower() in answer_lower)
    return matches / len(keywords)
    return "", [], 0.0
def compute_faithfulness(answer: str, sources: list[dict]) -> bool:
    answer_lower = answer.lower()
    for source in sources[:3]:
        if not isinstance(source, dict):
            continue
        snippet = str(source.get("text", "") or "").lower().strip()
        if not snippet:
            continue
        snippet_prefix = snippet[:100].strip()
        if snippet_prefix and snippet_prefix in answer_lower:
            return True
    return False


def _extract_answer_and_sources(result) -> tuple[str, list[dict]]:
    if isinstance(result, tuple) and len(result) >= 2:
        answer = str(result[0] or "")
        sources = result[1] if isinstance(result[1], list) else []
        return answer, sources

    if isinstance(result, dict):
        answer = str(result.get("answer", "") or "")
        raw_sources = result.get("sources", [])
        sources = raw_sources if isinstance(raw_sources, list) else []
        return answer, sources

    return "", []


def evaluate() -> None:
    correct = 0
    total = len(test_data)
    total_time = 0.0
    relevance_scores: list[float] = []
    faithful_count = 0
    confidence_scores: list[float] = []
    total_time = 0.0
    if total == 0:

    if total_questions == 0:
        print("No test data available.")
    for item in test_data:
        question = str(item.get("question", "") or "").strip()
        keywords = [str(k).strip().lower() for k in item.get("keywords", []) if str(k).strip()]
        question = str(item.get("question", "") or "").strip()
        keywords = [str(k).lower().strip() for k in item.get("keywords", []) if str(k).strip()]

        start = time.time()
        result = answer_query(question)
        end = time.time()

        answer, sources = _extract_answer_and_sources(result)
        latency = end - start
        confidence_scores.append(confidence)
        if any(k in answer_lower for k in keywords):
            correct += 1

        rel = compute_relevance(answer, keywords)
        relevance_scores.append(rel)

        if compute_faithfulness(answer, sources):
            faithful_count += 1

        try:
            score_values = []
            for source in sources[:3]:
                if isinstance(source, dict):
                    score_values.append(float(source.get("score", 0) or 0))
            conf = (sum(score_values) / len(score_values)) * 100 if score_values else 0.0
        except Exception:
            conf = 0.0
        if is_correct:
        confidence_scores.append(conf)

        print(f"\nQ: {question}")
        print(f"\n[{idx}/{total_questions}] {status}")
        print(f"Question: {question}")
        else:

        print("-" * 40)

    accuracy = (correct / total) * 100
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    faithfulness_rate = (faithful_count / total) * 100
    avg_latency = total_time / total
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

    print("\n===== ADVANCED RAG EVALUATION =====")
    avg_latency = total_time / total_questions
    print(f"Relevance: {avg_relevance:.2f}")
    print(f"Faithfulness: {faithfulness_rate:.2f}%")
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

    print("\n===== RAG EVALUATION =====")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Avg Latency: {avg_latency:.2f}s")
    evaluate()


if __name__ == "__main__":
    evaluate_rag()
