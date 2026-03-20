from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from pypdf import PdfReader

# =========================
# PDF LOADER (RUN ONCE)
# =========================
def load_pdf_chunks(path):
    try:
        reader = PdfReader(path)
        text = ""

        for page in reader.pages:
            try:
                text += page.extract_text() or ""
            except:
                continue

        if not text.strip():
            print(f"WARNING: No text extracted from {path}")
            return []

        chunk_size = 500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        return chunks[:5]

    except Exception as e:
        print(f"PDF LOAD ERROR ({path}):", e)
        return []


# 🔥 LOAD ON START (IMPORTANT)
pdf_chunks = (
    load_pdf_chunks("data/raw/research_paper.pdf") +
    load_pdf_chunks("data/raw/BAJA SAEINDIA RULBOOK 2026_Rev01_00_1762695140.pdf")
)

baja_chunks = [
    "BAJA SAE is a collegiate engineering competition where students design, build, and race off-road vehicles.",
    "Teams must follow strict rules related to vehicle safety, engine specifications, and design constraints.",
    "The competition includes events like endurance race, maneuverability, suspension testing, and cost evaluation.",
    "All vehicles must comply with safety standards including roll cages, braking systems, and driver protection."
]

all_chunks = baja_chunks + pdf_chunks


# =========================
# FASTAPI SETUP
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CONTEXT_CHARS = 1200
MAX_SELECTED_CHUNKS = 3


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


# =========================
# MAIN API
# =========================
@app.post("/query")
def query(q: QueryRequest):

    # =========================
    # Step 1: Retrieval
    # =========================
    query_lower = q.query.lower()
    keywords = [w for w in query_lower.split() if len(w) > 2]

    filtered = [
        c for c in all_chunks
        if any(word in c.lower() for word in keywords)
    ]

    selected_chunks = filtered[:MAX_SELECTED_CHUNKS] if filtered else all_chunks[:MAX_SELECTED_CHUNKS]

    context = "\n".join(selected_chunks)[:MAX_CONTEXT_CHARS]

    if not context.strip():
        context = "No context available"

    # =========================
    # Step 2: Prompt
    # =========================
    prompt = f"""
Answer ONLY using the context.

Context:
{context}

Question: {q.query}

Answer (3-5 lines):
"""

    # =========================
    # Step 3: LLM CALL (FAST)
    # =========================
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "phi",   # 🔥 FAST MODEL
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 50,
                    "temperature": 0.1
                }
            },
            timeout=20   # 🔥 IMPORTANT
        )

        if response.status_code != 200:
            answer = context
        else:
            data = response.json()
            answer = data.get("response", "").strip()

    except:
        # 🔥 NEVER FAIL UI
        answer = context

    # =========================
    # Step 4: Format
    # =========================
    answer = answer.replace(". ", ".\n\n")
    answer = f"### 📌 Answer\n\n{answer}"

    # =========================
    # Step 5: Sources
    # =========================
    sources = [
        {"content": c, "document": f"Chunk {i+1}", "score": 1.0}
        for i, c in enumerate(selected_chunks)
    ]

    return {
        "answer": answer,
        "sources": sources,
        "confidence": 0.8
    }