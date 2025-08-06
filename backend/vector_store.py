# vector_store.py
import numpy as np
from embeddings import embed_text
from typing import List

class InMemoryStore:
    def __init__(self):
        self.docs: List[str] = []
        self.embeddings: np.ndarray | None = None

    async def ingest(self, texts: List[str]) -> int:
        resp_data = await embed_text(texts)
        embs = np.array([item["embedding"] for item in resp_data])
        self.docs.extend(texts)
        if self.embeddings is None:
            self.embeddings = embs
        else:
            self.embeddings = np.vstack((self.embeddings, embs))
        return len(texts)

    async def query(self, text: str, top_k: int = 3):
        resp_data = await embed_text([text])
        emb = np.array(resp_data[0]["embedding"])
        sims = (self.embeddings @ emb) / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(emb))
        top_ids = np.argsort(-sims)[:top_k]
        return [(self.docs[i], float(sims[i])) for i in top_ids]
