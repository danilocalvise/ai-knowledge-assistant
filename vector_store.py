# vector_store.py
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class InMemoryStore:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.embedder = SentenceTransformer(model_name)
        self.docs: List[str] = []
        self.embeddings: np.ndarray = np.empty((0, self.embedder.get_sentence_embedding_dimension()))

    def ingest(self, texts: List[str]):
        embeddings = self.embedder.encode(texts)
        self.docs.extend(texts)
        if self.embeddings.size == 0:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack((self.embeddings, embeddings))
        return len(texts)

    def query(self, text: str, top_k=3):
        q_emb = self.embedder.encode([text])[0]
        sims = (self.embeddings @ q_emb) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_emb)
        )
        top_ids = np.argsort(-sims)[:top_k]
        return [(self.docs[i], float(sims[i])) for i in top_ids]
