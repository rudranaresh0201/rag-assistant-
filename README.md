**RAG Assistant**



**BAJA RAG Assistant**

&#x20;**Demo**



**### Frontend**

**<img src="https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/rag-frontend.png" width="800"/>**



**### Backend**

**<img src="https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/rag-backend.png" width="800"/>**



**### Retrieval**

**<img src="https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/source-retrieval.png" width="800"/>**



**This is a full-stack Retrieval-Augmented Generation (RAG) system for querying BAJA SAE rulebooks and technical documents using natural language.**



**Built using FastAPI, React, ChromaDB, and a local LLM (phi3 via Ollama), it gives answers grounded in actual document content instead of guessing.**







**Overview**



**The idea is simple: instead of manually searching PDFs, you can just ask a question like:**



**"What are the safety rules in BAJA?"**



**and the system will return:**



**\* a context-based answer**

**\* relevant document chunks**

**\* retrieval scores for transparency**







**How it works**



**\* User sends a query**

**\* Query is converted into embeddings**

**\* Top relevant chunks are retrieved from the vector database**

**\* These chunks are passed to the LLM**

**\* The LLM generates a grounded answer**



**This reduces hallucination and makes outputs more traceable.**







**Tech stack**



**Backend**



**\* FastAPI (Python)**



**Frontend**



**\* React (Vite)**

**\* Tailwind CSS**



**AI / ML**



**\* Sentence Transformers (embeddings)**

**\* ChromaDB (vector database)**

**\* Ollama (phi3 - local LLM)**







**Setup**



**1. Clone the repo**

&#x20;  **git clone https://github.com/rudranaresh0201/rag-assistant-.git**

&#x20;  **cd rag-assistant-**



**2. Backend**

&#x20;  **pip install -r requirements.txt**

&#x20;  **uvicorn api:app --reload**



**3. Run LLM**

&#x20;  **ollama run phi3**



**4. Frontend**

&#x20;  **cd frontend**

&#x20;  **npm install**

&#x20;  **npm run dev**



**5. Open**

&#x20;  **http://localhost:5173**





**Example**



**Input**

**What are the safety rules in BAJA?**



**Output**



**\* Generated answer**

**\* Supporting document chunks**

**\* Retrieval scores**







**Future improvements**



**\* Better retrieval (reranking)**

**\* Multi-document support**

**\* Deployment (Render / Vercel)**

**\* Voice input**

**\* Caching**





**Author**



**Rudra Naresh**

**Electronics Engineering, VJTI**

