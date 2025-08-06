from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.vector_store import InMemoryStore
from app.llm_service import generate_answer
from app.file_processor import FileProcessor
from app.chunking_service import ChunkingService
import tempfile
import os
from typing import List, Optional

class IngestRequest(BaseModel):
    documents: list[str]

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

class UploadResponse(BaseModel):
    filename: str
    file_type: str
    chunks_created: int
    metadata: dict

app = FastAPI(title="AI Knowledge Assistant API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = InMemoryStore()
file_processor = FileProcessor()
chunking_service = ChunkingService()

@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file (PDF, DOCX, Markdown, or text)"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        try:
            # Process the file
            content_chunks, metadata = file_processor.process_file(temp_file_path)
            
            # Create enhanced chunks
            enhanced_chunks = chunking_service.create_smart_chunks(
                content_chunks, metadata, preserve_structure=True
            )
            
            # Extract text for vector store
            chunk_texts = [chunk.text for chunk in enhanced_chunks]
            
            # Store in vector database
            count = await store.ingest_with_metadata(chunk_texts, enhanced_chunks)
            
            return UploadResponse(
                filename=file.filename,
                file_type=metadata.file_type,
                chunks_created=count,
                metadata={
                    "title": metadata.title,
                    "author": metadata.author,
                    "pages": metadata.pages,
                    "file_size": metadata.file_size,
                    "created_date": metadata.created_date.isoformat() if metadata.created_date else None
                }
            )
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/ingest")
async def ingest(req: IngestRequest):
    """Legacy endpoint for ingesting plain text documents"""
    count = await store.ingest(req.documents)
    return {"ingested": count}

@app.post("/api/query")
async def query(req: QueryRequest):
    """Query the knowledge base and get AI-generated answers"""
    docs = await store.query(req.query, req.top_k)
    snippets = [doc for doc, _ in docs]
    answer = await generate_answer(snippets, req.query)
    
    # Enhanced response with metadata
    results_with_metadata = []
    for doc, score in docs:
        chunk_metadata = store.get_chunk_metadata(doc)
        results_with_metadata.append({
            "text": doc,
            "score": score,
            "metadata": chunk_metadata
        })
    
    return {
        "results": results_with_metadata,
        "answer": answer,
        "total_results": len(docs)
    }

@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents with their metadata"""
    return await store.get_documents_list()

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and all its chunks"""
    deleted_count = await store.delete_document(doc_id)
    return {"deleted_chunks": deleted_count, "document_id": doc_id}

@app.get("/api/stats")
async def get_stats():
    """Get knowledge base statistics"""
    return store.get_document_stats()

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000)
