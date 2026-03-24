import chromadb
from sentence_transformers import SentenceTransformer

# Global variables
model = None
collection = None


def init_vector_store():
    global model, collection

    if model is None:
        print("🔄 Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')

    if collection is None:
        print("📦 Initializing ChromaDB...")
        client = chromadb.Client()
        collection = client.get_or_create_collection(name="rag_collection")


# =========================
# ADD CHUNKS (BATCHED)
# =========================
def add_chunks(chunks):
    init_vector_store()

    if not chunks:
        return

    print(f"📥 Adding {len(chunks)} chunks...")

    batch_size = 32  # 🔥 prevents memory crash

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        embeddings = model.encode(batch).tolist()
        ids = [f"id_{i+j}" for j in range(len(batch))]

        collection.add(
            documents=batch,
            embeddings=embeddings,
            ids=ids
        )

    print(f"✅ Added {len(chunks)} chunks in batches")


# =========================
# QUERY CHUNKS
# =========================
def query_chunks(query, n_results=3):
    init_vector_store()

    if not query:
        return []

    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    return results.get('documents', [[]])[0]