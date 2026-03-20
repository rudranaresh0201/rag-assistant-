"""
config/settings.py
------------------
Central configuration for the entire RAG application.

All tuneable parameters live here so you never have to hunt through
source files to change a model name, a path, or a chunk size.
"""

from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
# BASE_DIR resolves to:  rag_app/   (two levels up from this file)
BASE_DIR        = Path(__file__).resolve().parent.parent.parent
DATA_DIR        = BASE_DIR / "data"
RAW_DOCS_DIR    = DATA_DIR / "raw"          # put your PDFs / TXTs here
VECTORSTORE_DIR = DATA_DIR / "vectorstore"  # FAISS index is saved here

# ── Embedding model ────────────────────────────────────────────────────────────
# all-MiniLM-L6-v2:  22 M params, 384-dim vectors, fast on CPU, great quality
EMBEDDING_MODEL     = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ── Chunking ──────────────────────────────────────────────────────────────────
# Smaller chunks → better precision but more vectors stored.
# Larger chunks → more context per chunk but noisier retrieval.
CHUNK_SIZE    = 500   # characters per chunk
CHUNK_OVERLAP = 50    # overlap keeps context continuous across boundaries

# ── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K_RESULTS = 5     # number of chunks returned for every query

# ── Generation model ──────────────────────────────────────────────────────────
# google/flan-t5-base:  250 M params, instruction-tuned, runs well on CPU,
#                       downloads automatically from Hugging Face (~1 GB).
# Swap for a larger model (flan-t5-large, flan-t5-xl) if you have more RAM.
GENERATION_MODEL = "google/flan-t5-base"
MAX_NEW_TOKENS   = 512
TEMPERATURE      = 0.2  # lower = more factual / less creative

# ── Vector store filenames ────────────────────────────────────────────────────
FAISS_INDEX_FILE = "faiss_index"    # binary FAISS index
METADATA_FILE    = "metadata.json"  # chunk texts + metadata
