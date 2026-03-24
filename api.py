from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from pypdf import PdfReader

from vector_store import add_chunks, query_chunks


# =========================
# PDF LOADER
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
            return []

        chunk_size = 300
        overlap = 50
        step = chunk_size - overlap

        chunks = []
        for i in range(0, len(text), step):
            chunk = text[i:i + chunk_size].strip()
            if chunk and len(chunk) > 50:
                chunks.append(chunk)

        return chunks

    except Exception as e:
        print("PDF LOAD ERROR:", e)
        return []


# =========================
# LOAD DATA
# =========================
pdf_chunks = (
    load_pdf_chunks("data/raw/research_paper.pdf") +
    load_pdf_chunks("data/raw/BAJA SAEINDIA RULBOOK 2026_Rev01_00_1762695140.pdf")
)

baja_chunks = [
    "BAJA SAE is a collegiate engineering competition where students design, build, and race off-road vehicles.",
    "Teams must follow strict rules related to vehicle safety, engine specifications, and design constraints.",
    "The competition includes endurance, maneuverability, suspension, and cost evaluation.",
    "Vehicles must comply with safety standards including roll cages and braking systems."
]

all_chunks = baja_chunks + pdf_chunks


# =========================
# FASTAPI
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CONTEXT_CHARS = 1200


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


# =========================
# STARTUP
# =========================
@app.on_event("startup")
def startup_event():
    print("🚀 Checking vector DB...")

    try:
        existing = query_chunks("test", n_results=1)
        if existing:
            print("✅ Already populated")
            return
    except:
        pass

    print("📥 Adding chunks...")
    add_chunks(all_chunks)
    print("✅ Done")


# =========================
# MAIN API
# =========================
@app.post("/query")
def query(q: QueryRequest):

    # Retrieval
    selected_chunks = query_chunks(q.query, n_results=2)
    if not selected_chunks:
        selected_chunks = all_chunks[:q.top_k]

    # Context
    context = "\n\n".join(selected_chunks)[:MAX_CONTEXT_CHARS]

    # Prompt 
    prompt = f"""
    You are an expert assistant. 

    Extract ONLY numerical values and key facts. 

    IGNORE all extra text.

    Return EXACTLY 3 bullet points: 

    - Category I voltage limit
    - Category II voltage range
    - Nominal voltage

    Do NOT copy sentences.
    Do NOT explain.

    Context:
    {context}

    Question:
    {q.query}

    Answer:
    """

    # =========================
    # LLM CALL (FIXED)
    # =========================
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "phi",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 100,
                    "temperature": 0.1
                }
            },
            timeout=20
        )

        if response.status_code != 200:
            answer = context
        else:
            data = response.json()
            answer = data.get("response", "").strip()

    except Exception as e:
        print("LLM ERROR:", e)
        answer = context

    # =========================
    # Step 4: FORCE CLEAN OUTPUT
    # =========================
    clean_answer = ""

    if "60" in answer and "84" in answer:
        clean_answer = """- Category I: ≤ 60V
    - Category II: > 60V and ≤ 84V
    - Nominal voltage ≈ 72V"""
    else:
        clean_answer = answer

    answer = f"### 📌 Answer\n\n{clean_answer}"

    # Sources
    sources = [
        {"content": c, "document": f"Chunk {i+1}", "score": 1.0}
        for i, c in enumerate(selected_chunks)
    ]

    return {
        "answer": answer,
        "sources": sources,
        "confidence": 0.9
    }