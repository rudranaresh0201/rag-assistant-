&#x20;**RAG Assistant**



**A full-stack Retrieval-Augmented Generation (RAG) system that enables users to query BAJA SAE rulebooks and research documents using natural language.**



**Built with FastAPI, React, ChromaDB, and a local LLM (Ollama).**



&#x20;**Features**



&#x20;**Semantic search over PDFs (rulebooks and research papers)**

&#x20;**Local LLM inference using Ollama (no external API required)**

&#x20;**Source-aware answers with multiple retrieved document chunks**

&#x20;**Displays top-k sources (e.g., Chunk 1, Chunk 2) used to generate the answer**

&#x20;**Confidence scoring for retrieved results**

&#x20;**Fast retrieval using Chroma vector database**

&#x20;**Clean React-based chat interface**

&#x20;**End-to-end RAG pipeline (ingestion → retrieval → generation)**







&#x20;**Demo**

&#x20;**Demo**



**## Demo**



**### Chat Interface**



**!\[RAG Frontend](assets/screenshots/rag-frontend.png)**



**### Retrieved Sources (RAG Evidence)**



**!\[Source Retrieval](assets/screenshots/source-retrieval.png)**



**### Backend API Response**



**!\[RAG Backend](assets/screenshots/rag-backend.png)User Query**

&#x20;  **↓**

**React Frontend**

&#x20;  **↓**

**FastAPI Backend (/query)**

&#x20;  **↓**

**Retriever (ChromaDB)**

&#x20;  **↓**

**Context Builder**

&#x20;  **↓**

**LLM (Ollama - phi3)**

&#x20;  **↓**

**Answer + Sources + Confidence**

**```**







**How Retrieval Works**



**For each user query:**



**1. The system retrieves the top-k most relevant chunks from the document corpus**

**2. Each chunk is labeled (e.g., Chunk 1, Chunk 2)**

**3. These chunks are passed as context to the LLM**

**4. The final answer is generated using only this retrieved context**



**This ensures:**



&#x20;**Transparency (users can see exactly where answers come from)**

**Reduced hallucination**

**\*Traceability of information sources**





**Tech Stack**



&#x20;**Backend**



**FastAPI**

&#x20;**Python**

&#x20;**ChromaDB**

&#x20;**Sentence Transformers**

&#x20;**Ollama (phi3)**



&#x20;**Frontend**



&#x20;**React (Vite)**

&#x20;**Tailwind CSS**





&#x20;**Setup Instructions**



&#x20;**1. Clone the repository**





**git clone https://github.com/rudranaresh0201/rag-assistant-.git**

**cd rag-assistant-**











&#x20;**2. Backend setup**





**pip install -r requirements.txt**

**uvicorn api:app --reload**

&#x20;**3. Run Ollama**

**ollama run phi3**

**4. Frontend setup**

**cd frontend**

**npm install**

**npm run dev**

&#x20;**5. Open the application**

**http://localhost:5173**



**Example Query**



**"What are safety rules in BAJA?"**



**Returns:**

&#x20;**Generated answer**

**Retrieved document chunks (e.g., Chunk 1, Chunk 2)**

**Confidence score**







**Future Improvements**



&#x20;**Deployment (Render for backend, Vercel for frontend)**

&#x20;**Improved reranking using cross-encoders**

**Multi-document upload interface**

**Voice-based querying**

&#x20;**Performance optimization and caching**







**Author**



**Rudra Naresh**

**VJTI Electronics SY**

