**RAG Assistant**
A full-stack RAG-powered assistant that allows users to query documents using a local LLM (phi3 via Ollama), ensuring privacy and fast responses.



**BAJA RAG Assistant**

&#x20;**Demo**



Frontend

**<img src="https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/rag-frontend.png" width="800"/>**



Backend

**<img src="https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/rag-backend.png" width="800"/>**



 Retrieval

**<img src="https://raw.githubusercontent.com/rudranaresh0201/rag-assistant-/main/assets/screenshots/source-retrieval.png" width="800"/>**



**This is a full-stack Retrieval-Augmented Generation (RAG) system for querying BAJA SAE rulebooks and technical documents using natural language.**

**Built using FastAPI, React, ChromaDB, and a local LLM (phi3 via Ollama), it gives answers grounded in actual document content instead of guessing.**




**Overview**
**The idea is simple: instead of manually searching PDFs, you can just ask a question like:**
**"What are the safety rules in BAJA?"**
**and the system will return:**
** a context-based answer**
** relevant document chunks**
**retrieval scores for transparency**


##  How It Works

1. Documents are uploaded and split into smaller chunks  
2. Chunks are converted into embeddings using Sentence Transformers  
3. Embeddings are stored in ChromaDB (vector database)  
4. User query is embedded and matched with relevant chunks via similarity search  
5. Ollama (phi3) generates context-aware answers using retrieved data  
6. Final response is returned to the user through the frontend

##  Tech Stack

**Backend**
- FastAPI (Python)

**Frontend**
- React (Vite)
- Tailwind CSS

**AI / ML**
- Sentence Transformers (embeddings)
- ChromaDB (vector database)
- Ollama (phi3 - local LLM)


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
 Generated answer
Supporting document chunks
Retrieval scores

**Future improvements**
Better retrieval (reranking)
 Multi-document support
 Deployment (Render / Vercel)
 Voice input
Caching

**Author**
**Rudra Naresh**
**Electronics Engineering, VJTI**

