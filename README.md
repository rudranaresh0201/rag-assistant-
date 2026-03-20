&#x20;**RAG Assistant**



**A full-stack Retrieval-Augmented Generation (RAG) system that enables users to query BAJA SAE rulebooks and research documents using natural language.**



**Built with FastAPI, React, ChromaDB, and a local LLM (Ollama).**



**---**



**## Features**



**\* Semantic search over PDFs (rulebooks and research papers)**

**\* Local LLM inference using Ollama (no external API required)**

**\* Source-aware answers with multiple retrieved document chunks**

**\* Displays top-k sources (e.g., Chunk 1, Chunk 2) used to generate the answer**

**\* Confidence scoring for retrieved results**

**\* Fast retrieval using Chroma vector database**

**\* Clean React-based chat interface**

**\* End-to-end RAG pipeline (ingestion → retrieval → generation)**



**---**



**## Demo**



**### Chat Interface**

**!\[RAG Frontend](assets/screenshots/rag-frontend.png)**



**### Retrieved Sources (RAG Evidence)**

**!\[Source Retrieval](assets/screenshots/source-retrieval.png)**



**### Backend API Response**

**!\[RAG Backend](assets/screenshots/rag-backend.png)**

**---**



**## Architecture**



**```**

**User Query**

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



**---**



**## How Retrieval Works**



**For each user query:**



**1. The system retrieves the top-k most relevant chunks from the document corpus**

**2. Each chunk is labeled (e.g., Chunk 1, Chunk 2)**

**3. These chunks are passed as context to the LLM**

**4. The final answer is generated using only this retrieved context**



**This ensures:**



**\* Transparency (users can see exactly where answers come from)**

**\* Reduced hallucination**

**\* Traceability of information sources**



**---**



**## Tech Stack**



**### Backend**



**\* FastAPI**

**\* Python**

**\* ChromaDB**

**\* Sentence Transformers**

**\* Ollama (phi3)**



**### Frontend**



**\* React (Vite)**

**\* Tailwind CSS**



**---**



**## Setup Instructions**



**### 1. Clone the repository**



**```**

**git clone https://github.com/rudranaresh0201/rag-assistant-.git**

**cd rag-assistant-**

**```**



**---**



**### 2. Backend setup**



**```**

**pip install -r requirements.txt**

**uvicorn api:app --reload**

**```**



**---**



**### 3. Run Ollama**



**```**

**ollama run phi3**

**```**



**---**



**### 4. Frontend setup**



**```**

**cd frontend**

**npm install**

**npm run dev**

**```**



**---**



**### 5. Open the application**



**```**

**http://localhost:5173**

**```**



**---**



**## Example Query**



**"What are safety rules in BAJA?"**



**Returns:**



**\* Generated answer**

**\* Retrieved document chunks (e.g., Chunk 1, Chunk 2)**

**\* Confidence score**



**---**



**## Future Improvements**



**\* Deployment (Render for backend, Vercel for frontend)**

**\* Improved reranking using cross-encoders**

**\* Multi-document upload interface**

**\* Voice-based querying**

**\* Performance optimization and caching**



**---**



**## Author**



**Rudra Naresh**

**VJTI Electronics SY** 

