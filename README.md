

&#x20;**RAG Assistant**

**# BAJA RAG Assistant**



**!\[Frontend](assets/screenshots/rag-frontend.png)**

**!\[Backend](assets/screenshots/rag-backend.png)**

**!\[Retrieval](assets/screenshots/source-retrieval.png)**



**!A full-stack Retrieval-Augmented Generation (RAG) system for querying BAJA SAE rulebooks and research documents using natural language. Built with FastAPI, React, ChromaDB, and a local LLM via Ollama.**



**---**



**What it does**



**This system retrieves information from multiple sources, including:**



**\* BAJA SAE rulebook**

**\* Research paper: https://arxiv.org/pdf/2108.05877**



**A user can ask questions like "What are the safety rules in BAJA?" and receive:**



**\* A grounded answer generated from retrieved context**

**\* Labeled source references (Chunk 1, Chunk 2, etc.)**

**\* A retrieval score indicating relevance**



**---**



**Features**



**\* Natural language search over PDFs**

**\* Local inference using Ollama (phi3)**

**\* Source-aware answers with retrieved document chunks**

**\* Retrieval score for relevance**

**\* Fast semantic retrieval using ChromaDB**

**\* Clean React UI with Tailwind CSS**

**\* End-to-end RAG pipeline**



**---**



**----**



**Demo**



**Chat Interface**



**!\[RAG Frontend](assets/screenshots/rag-frontend.png)**



**Source Retrieval**



**!\[Source Retrieval](assets/screenshots/source-retrieval.png)**



**Backend API Response**



**!\[RAG Backend](assets/screenshots/rag-backend.png)**



**---**



**Architecture**



**User Query**

**↓**

**React Frontend**

**↓**

**FastAPI Backend (/query)**

**↓**

**Retriever (ChromaDB)**

**↓**

**Context Builder**

**↓**

**LLM (Ollama — phi3)**

**↓**

**Answer + Sources + Score**





**How Retrieval Works**



**\* Converts query into embeddings**

**\* Retrieves top-k relevant chunks**

**\* Labels chunks (Chunk 1, Chunk 2...)**

**\* Generates answer using retrieved context**



**This improves traceability and reduces hallucination.**



**---**



**Tech Stack**



**Backend: FastAPI, Python**

**Vector DB: ChromaDB**

**Embeddings: Sentence Transformers**

**LLM: Ollama (phi3)**

**Frontend: React (Vite), Tailwind CSS**



**---**



**Setup**



**Clone:**

**git clone https://github.com/rudranaresh0201/rag-assistant-.git**

**cd rag-assistant-**



**Backend:**

**pip install -r requirements.txt**

**uvicorn api:app --reload**



**LLM:**

**ollama run phi3**



**Frontend:**

**cd frontend**

**npm install**

**npm run dev**



**Open:**

**http://localhost:5173**



**---**



**Example**



**Query: "What are safety rules in BAJA?"**



**Returns:**



**\* Generated answer**

**\* Source chunks**

**\* Retrieval score**



**---**



**What's Next**



**\* Deployment (Render + Vercel)**

**\* Reranking (cross-encoder)**

**\* Multi-document upload UI**

**\* Voice querying**

**\* Caching layer**



**---**



**Built by Rudra Naresh**

**Electronics Engineering, VJTI**

