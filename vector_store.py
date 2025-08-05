# vector_store.py
import numpy as np
from embeddings import embed_text
from typing import List

class InMemoryStore:
    def __init__(self):
        self.docs: List[str] = []
        self.embeddings: np.ndarray = np.empty((0,))  # shape later

    async def ingest(self, texts: List[str]) -> int:
        embs = await embed_text(texts)
        vecs = np.array(embs)
        self.docs.extend(texts)
        if self.embeddings.size == 0:
            self.embeddings = vecs
        else:
            self.embeddings = np.vstack((self.embeddings, vecs))
        return len(texts)

    async def query(self, text: str, top_k: int = 3):
        emb = await embed_text(text)
        emb = np.array(emb)
        # compute cosine similarity
        sims = (self.embeddings @ emb) / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(emb))
        top_ids = np.argsort(-sims)[:top_k]
        return [(self.docs[i], float(sims[i])) for i in top_ids]
