from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

# Import our RAG logic
from ingest import ingest_docs
from query import query_rag

app = FastAPI(
    title="Local RAG API",
    description="Production-ready API for Local Retrieval-Augmented Generation",
    version="1.0.0"
)

# Data Models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

class HealthResponse(BaseModel):
    status: str
    model: str
    database_found: bool

@app.get("/", tags=["General"])
async def root():
    return {"message": "Welcome to the Local RAG API. Use /docs for documentation."}

@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    db_exists = os.path.exists("vector_db")
    return {
        "status": "healthy",
        "model": "llama3",
        "database_found": db_exists
    }

@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def ask_question(request: QueryRequest):
    try:
        # Check if DB exists
        if not os.path.exists("vector_db"):
            raise HTTPException(status_code=404, detail="Vector database not found. Please run /ingest first.")
        
        result = query_rag(request.question)
        
        sources = [doc.metadata.get('source', 'Unknown') for doc in result["context"]]
        # Deduplicate sources
        sources = list(set(sources))
        
        return {
            "answer": result["answer"],
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest", tags=["Management"])
async def run_ingestion():
    try:
        # This will process files in the /docs folder
        ingest_docs()
        return {"message": "Ingestion successful. Vector database updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
