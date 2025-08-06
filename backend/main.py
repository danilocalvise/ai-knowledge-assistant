from fastapi import FastAPI
from pydantic import BaseModel
from vector_store import InMemoryStore
from llm_service import generate_answer

class IngestRequest(BaseModel):
    documents: list[str]

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

app = FastAPI()
store = InMemoryStore()

@app.post("/api/ingest")
async def ingest(req: IngestRequest):
    count = await store.ingest(req.documents)
    return {"ingested": count}

@app.post("/api/query")
async def query(req: QueryRequest):
    docs = await store.query(req.query, req.top_k)
    snippets = [doc for doc, _ in docs]
    answer = await generate_answer(snippets, req.query)
    return {"results": docs, "answer": answer}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000)
