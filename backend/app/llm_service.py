import os, httpx


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-4o"  # or gpt-3.5-turbo

async def generate_answer(contexts: list[str], query: str) -> str:
    snippets = "\n\n".join(contexts)
    prompt = f"""You are a helpful assistant that answers technical questions using the document context below.
    If answer is not in context, say "I don't know." Use bullet points.
    
    Context:
    \"\"\"{snippets}\"\"\"

    User Query:
    \"{query}\"

    Answer:"""

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": GPT_MODEL, "messages": [{"role":"system", "content":prompt}]}
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
