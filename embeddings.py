# embeddings.py
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Get the base directory of the project
BASE_DIR = Path(__file__).parent

# Load environment variables from .env file if it exists
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
EMBEDDING_MODEL = "text-embedding-3-small"

async def embed_text(texts: list[str]) -> list[list[float]]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": EMBEDDING_MODEL, "input": texts}
        )
        resp.raise_for_status()
        return resp.json()["data"]
