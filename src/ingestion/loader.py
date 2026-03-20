"""
src/ingestion/loader.py
-----------------------
Loads raw documents (PDF, TXT, Markdown) from the data/raw/ directory.

Each document is returned as a simple Python dict:
    {
        "content":  str,   ← the full text of the document
        "metadata": dict   ← source filename, type, path
    }

Supported formats:
    .txt  – plain text
    .md   – Markdown
    .rst  – reStructuredText
    .pdf  – PDF (requires 'pypdf' package)

Why keep loading separate from chunking?
    Single-responsibility principle: loaders only read files.
    You can swap out the loader (e.g. add Word/HTML support) without
    touching any downstream code.
"""

import logging
from pathlib import Path

from src.config.settings import RAW_DOCS_DIR
from src.types import Document

logger = logging.getLogger(__name__)

# Optional PDF support – gracefully degrade if pypdf isn't installed
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


# ── Low-level readers ─────────────────────────────────────────────────────────

def load_text_file(file_path: Path) -> str:
    """Read a plain-text / Markdown / RST file and return its content."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def load_pdf_file(file_path: Path) -> str:
    """
    Extract text from a PDF, page by page.

    Pages are joined with double newlines so the chunker can later split
    on natural paragraph boundaries.
    """
    if not PDF_SUPPORT:
        raise ImportError(
            "pypdf is required to load PDF files.  "
            "Install it with:  pip install pypdf"
        )
    reader = PdfReader(str(file_path))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            pages.append(text.strip())
    return "\n\n".join(pages)


# ── Document-level loader ─────────────────────────────────────────────────────

def load_document(file_path: Path) -> Document:
    """
    Load a single document and return a structured dict.

    Args:
        file_path:  pathlib.Path pointing to the document

    Returns:
        {
            "content":  str,                    # full extracted text
            "metadata": {
                "source":    str,               # file name (e.g. 'report.pdf')
                "file_type": str,               # extension (e.g. '.pdf')
                "file_path": str,               # absolute path as string
            }
        }

    Raises:
        ValueError if the file extension is not supported.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        content = load_pdf_file(file_path)
    elif suffix in (".txt", ".md", ".rst"):
        content = load_text_file(file_path)
    else:
        raise ValueError(
            f"Unsupported file type '{suffix}' for file: {file_path.name}\n"
            "Supported: .txt, .md, .rst, .pdf"
        )

    return {
        "content": content,
        "metadata": {
            "source":    file_path.name,
            "file_type": suffix,
            "file_path": str(file_path.resolve()),
        },
    }


# ── Directory-level loader ────────────────────────────────────────────────────

def load_all_documents(directory: Path = RAW_DOCS_DIR) -> list[Document]:
    """
    Load every supported document in *directory*.

    Args:
        directory:  Path to the folder that holds raw documents.
                    Defaults to data/raw/ defined in settings.

    Returns:
        List of document dicts (see load_document).
    """
    supported = {".pdf", ".txt", ".md", ".rst"}
    documents: list[Document] = []

    if not directory.exists():
        raise FileNotFoundError(
            f"Document directory not found: {directory}\n"
            "Create the folder and add your documents there."
        )

    files = [f for f in directory.iterdir()
             if f.is_file() and f.suffix.lower() in supported]

    if not files:
        logger.warning("No supported documents found in: %s", directory)
        return documents

    for file_path in sorted(files):
        try:
            doc = load_document(file_path)
            documents.append(doc)
            logger.info(
                "Loaded '%s' (%s chars)",
                file_path.name,
                f"{len(doc['content']):,}",
            )
        except Exception as exc:
            logger.exception("Failed to load '%s': %s", file_path.name, exc)

    logger.info("Total documents loaded: %d", len(documents))
    return documents
