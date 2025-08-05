# embeddings.py
import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"  # Efficient & low-cost

async def embed_text(text: str) -> list[float]:
    resp = await httpx.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model": EMBEDDING_MODEL, "input": text}
    )
    resp.raise_for_status()
    data = resp.json()
    return data["data"][0]["embedding"]
