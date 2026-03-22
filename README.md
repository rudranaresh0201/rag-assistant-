&#x20;**RAG Assistant**

**# BAJA RAG Assistant**



**!\[Frontend](https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/rag-frontend.png)**



**!\[Backend](https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/rag-backend.png)**



**!\[Retrieval](https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/source-retrieval.png)**

**!**

**A full-stack Retrieval-Augmented Generation (RAG) system for querying BAJA SAE rulebooks and research documents using natural language. Built with FastAPI, React, ChromaDB, and a local LLM via Ollama.**



**---**



**# 🚀 BAJA RAG Assistant**



**A full-stack Retrieval-Augmented Generation (RAG) system for querying BAJA SAE rulebooks and technical research documents using natural language.**



**Built with FastAPI, React, ChromaDB, and a local LLM via Ollama, this system delivers grounded, source-aware answers with traceable retrieval.**



**---**



**##  Overview**



**This project enables users to interact with complex technical documents like BAJA SAE rulebooks through simple natural language queries.**



**Instead of manually searching PDFs, users can ask:**



**> "What are the safety rules in BAJA?"**



**and receive:**



**-  Context-grounded answers**  

**-  Source-referenced document chunks**  

**-  Retrieval relevance scores**  



**---**



**## ⚙️ Key Features**



**-  Semantic search over technical PDFs**  

**-  Retrieval-Augmented Generation (RAG pipeline)**  

**-  Source-aware answers with labeled chunks (Chunk 1, Chunk 2...)**  

**-  Retrieval scoring for transparency**  

**-  Fast vector search using ChromaDB**  

**-  Clean and responsive React UI (Tailwind CSS)**  

**-  Fully local LLM inference using Ollama (phi3)**  



**---**



**##  System Architecture**



**---**



**##  How It Works**



**1. User submits a query**  

**2. Query is converted into embeddings**  

**3. Top-k relevant document chunks are retrieved**  

**4. Chunks are labeled and structured**  

**5. LLM generates an answer using retrieved context**  



&#x20;**This ensures:**

**- Reduced hallucination**  

**- High traceability**  

**- Explainable outputs**  



**---**



**##  Tech Stack**



**\*\*Backend\*\***

**- FastAPI (Python)**



**\*\*Frontend\*\***

**- React (Vite)**

**- Tailwind CSS**



**\*\*AI/ML\*\***

**- Sentence Transformers (Embeddings)**

**- ChromaDB (Vector Database)**

**- Ollama (phi3 - Local LLM)**



**---**



**##  Setup Instructions**



**### 1. Clone the repository**

**```bash**

**git clone https://github.com/rudranaresh0201/rag-assistant-.git**

**cd rag-assistant-**

**2. Backend setup**

**pip install -r requirements.txt**

**uvicorn api:app --reload**

**3. Run LLM**

**ollama run phi3**

**4. frontend setup**

**cd frontend**

**npm install**

**npm run dev**

**5. open in browser** 

**http://localhost:5173**





**Example Query**



**Input:**



**What are the safety rules in BAJA?**



**Output:**



**Generated answer**

**Supporting document chunks**

**Retrieval relevance score**

&#x20;



**Future Improvements**

**Cross-encoder reranking for better retrieval accuracy**

**Multi-document upload support**

**Deployment (Render + Vercel)**

**Voice-based querying**

**Response caching layer**





**Author**



**Rudra Naresh**

**Electronics Engineering, VJTI**





