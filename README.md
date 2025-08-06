# AI Knowledge Assistant

A full-stack AI-powered chat assistant with a FastAPI backend and a Next.js (App Router) frontend. The backend provides LLM-powered document Q&A, and the frontend offers a real-time, streaming chat UI. Designed for easy deployment on Vercel.

---

## Features
- **Backend:** FastAPI, OpenAI LLM, vector search, `/api/query` endpoint
- **Frontend:** Next.js (App Router), Tailwind CSS, DaisyUI, real-time chat, token streaming
- **Deployment:** Vercel-ready, environment-based API routing

---

## Quick Start

### 1. Clone & Install
```sh
git clone <your-repo-url>
cd ai-knowledge-assistant
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install
```

### 2. Environment Variables

#### Backend (`backend/.env`):
```
OPENAI_API_KEY=sk-...your-key-here...
```

#### Frontend (`frontend/.env.local`):
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000/api/query
```

---

## Local Development

### Start the Backend
```sh
cd backend
# Make sure OPENAI_API_KEY is set in .env or your shell
test -f .env && export $(cat .env | xargs)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start the Frontend
```sh
cd frontend
npm run dev
```
- Open [http://localhost:3000](http://localhost:3000) to use the chat UI.

---

## Vercel Deployment

1. Push your code to GitHub (or your Vercel-connected repo).
2. Deploy the **frontend** on Vercel:
   - Set the environment variable in Vercel project settings:
     - `NEXT_PUBLIC_BACKEND_URL=https://<your-backend-domain>/api/query`
3. Deploy the **backend** (Vercel, Render, or your preferred host):
   - Set `OPENAI_API_KEY` in your backend host's environment variables.

---

## Environment Variables
- **Backend:** `OPENAI_API_KEY` (required)
- **Frontend:** `NEXT_PUBLIC_BACKEND_URL` (required for production)

---

## Endpoints
- `POST /api/query` (backend): Accepts `{ query: string, top_k?: int }`, returns `{ results, answer }`
- `POST /api/chat` (frontend): Proxies to backend, streams response for chat UI
- `GET /api/health` (backend): Health check

---

## Project Structure
```
ai-knowledge-assistant/
  backend/      # FastAPI app
  frontend/     # Next.js app (App Router)
```

---

## Notes
- The frontend will use the correct backend URL based on the environment variable.
- If `NEXT_PUBLIC_BACKEND_URL` is not set, it defaults to `http://localhost:8000/api/query` for local development.
- The backend requires a valid OpenAI API key.

---

For questions or issues, open an issue in this repo.
