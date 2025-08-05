from fastapi import FastAPI
from pydantic import BaseModel
from vector_store import InMemoryStore

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
    results = await store.query(req.query, req.top_k)
    return {"results": [{"doc": doc, "score": score} for doc, score in results]}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000)
