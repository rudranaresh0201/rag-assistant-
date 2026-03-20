from __future__ import annotations

import logging

from src.config.logging_config import configure_logging
from src.llm.generator import generate_answer
from src.qa import MAX_CONTEXT_LENGTH, build_context
from src.retrieval.retriever import retrieve

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    question = input("Ask a question: ").strip()

    if not question:
        print("Error: question cannot be empty")
        return

    logger.info("Starting retrieval step")
    retrieved_chunks = retrieve(question)

    if not retrieved_chunks:
        print("I could not find relevant context for your question.")
        return

    context, used_chunks = build_context(retrieved_chunks, max_length=MAX_CONTEXT_LENGTH)
    if not context.strip() or used_chunks == 0:
        print("I could not build enough context to answer your question.")
        return

    logger.info("Starting generation step")
    answer = generate_answer(question, context)

    print("\nANSWER:\n")
    print(answer)
    logger.info("Pipeline completed successfully using %d chunks", used_chunks)


if __name__ == "__main__":
    main()