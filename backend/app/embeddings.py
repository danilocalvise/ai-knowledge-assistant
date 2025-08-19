# embeddings.py
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Get the base directory of the project
BASE_DIR = Path(__file__).parent.parent

# Load environment variables from .env file if it exists
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"Attempting to load OpenAI API key...")

if not OPENAI_API_KEY:
    # Check if we're in a production environment
    if os.getenv("RENDER"):
        print("Running in Render environment, checking for API key...")
        # Try alternative environment variable names that might be used in Render
        OPENAI_API_KEY = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_SECRET_KEY")

if OPENAI_API_KEY:
    # Check key format and log safely (only show first 7 chars)
    key_start = OPENAI_API_KEY[:7] if len(OPENAI_API_KEY) > 7 else ""
    print(f"API key found. Starts with: {key_start}...")
    if not OPENAI_API_KEY.startswith("sk-"):
        print("Warning: API key doesn't start with 'sk-'. This might indicate an invalid key format.")
else:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your environment configuration.")

EMBEDDING_MODEL = "text-embedding-3-small"

async def embed_text(texts: list[str]) -> list[list[float]]:
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not configured. This might be due to an environment configuration issue.")
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Making request to OpenAI API with model: {EMBEDDING_MODEL}")
            # Log headers safely (excluding the actual key)
            auth_header = f"Bearer {OPENAI_API_KEY[:7]}..." if len(OPENAI_API_KEY) > 7 else "Bearer [hidden]"
            print(f"Using Authorization header format: {auth_header}")
            
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY.strip()}",  # Strip any whitespace
                    "Content-Type": "application/json"
                },
                json={"model": EMBEDDING_MODEL, "input": texts}
            )
            
            if resp.status_code == 401:
                error_msg = await resp.text()
                print(f"Authentication failed. Error details: {error_msg}")
                print("Please verify:\n1. API key format (should start with 'sk-')\n2. No whitespace in key\n3. Key is not expired")
                raise ValueError(f"OpenAI API authentication failed: {error_msg}")
                
            resp.raise_for_status()
            return resp.json()["data"]
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        print(f"An error occurred while calling OpenAI API: {str(e)}")
        raise
