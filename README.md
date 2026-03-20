**BAJA RAG Assistant**

&#x20;**BAJA RAG Assistant**



**!\[RAG Demo](assets/screenshots/rag-frontend.png)**





**A full-stack Retrieval-Augmented Generation (RAG) system for querying BAJA SAE rulebooks and research documents using natural language. Built with FastAPI, React, ChromaDB, and a local LLM via Ollama — no external API required.**



**What it does**

**This system retrieves information from multiple sources, including a research paper https://arxiv.org/pdf/2108.05877 and BAJA SAE rulebook** 

&#x20;**user Asks questions like "What are the safety rules in BAJA?" and gets back a grounded answer with the exact document chunks that were used to generate it. Every response includes a confidence score and labeled source references (Chunk 1, Chunk 2, etc.), so you always know where the information came from.**

&#x20;**Demo**



**Chat Interface**



**!\[RAG Frontend](assets/screenshots/rag-frontend.png)**



&#x20;**Source Retrieval**



**!\[Source Retrieval](assets/screenshots/source-retrieval.png)**



&#x20;**Backend API Response**



**!\[RAG Backend](assets/screenshots/rag-backend.png)**





**Natural language search over PDFs (rulebooks and research papers)**

**Local inference using Ollama with the phi3 model — everything runs on your machine**

**Source-aware answers with multiple retrieved document chunks displayed per response**

**Confidence scoring for retrieved results**

**Fast semantic retrieval via ChromaDB vector database**

**Clean React chat interface built with Vite and Tailwind CSS**

**End-to-end RAG pipeline — from document ingestion through retrieval to generation**





**Architecture**

**User Query**

&#x20;   **↓**

**React Frontend**

&#x20;   **↓**

**FastAPI Backend (/query)**

&#x20;   **↓**

**Retriever (ChromaDB)**

&#x20;   **↓**

**Context Builder**

&#x20;   **↓**

**LLM (Ollama — phi3)**

&#x20;   **↓**

**Answer + Sources + Confidence Score**



**How Retrieval Works**

**For each query, the system:**



**Converts your question into a vector embedding**

**Retrieves the top-k most semantically relevant chunks from the document corpus**

**Labels each chunk (Chunk 1, Chunk 2...) and passes them as context to the LLM**

**Generates a grounded answer using only what it actually found**



**This keeps answers traceable and reduces hallucination — the model can only reference what it actually retrieved.**



**Tech Stack**

**backend : fastapi, python**

**vector database: chromadb**

**embeddings: sentence Transformers**

**LLM: Ollama phi3**

**frontend: react(vite) , Tailwind css**









**1. Clone the repo**

**bashgit clone https://github.com/rudranaresh0201/rag-assistant-.git**

**cd rag-assistant-**

**2. Backend**

**bashpip install -r requirements.txt**

**uvicorn api:app --reload**

**3. Start Ollama**

**bashollama run phi3**

**4. Frontend**

**bashcd frontend**

**npm install**

**npm run dev**

**5. Open the app**

**http://localhost:5173**



**Example**

**Query: "What are safety rules in BAJA?"**

**Returns:**



**A generated answer grounded in the retrieved chunks**

**Labeled source excerpts (Chunk 1, Chunk 2...)**

**A confidence score for the retrieval**





**What's Next**

**A few things I'm planning to build out:**



**Deployment — Render for the backend, Vercel for the frontend**

**Reranking — cross-encoder reranking for better result ordering**

**Multi-document upload UI — drag-and-drop interface for adding new PDFs**

**Voice querying — speech-to-text input for hands-free use**

**Caching layer — avoid re-embedding repeated queries**

