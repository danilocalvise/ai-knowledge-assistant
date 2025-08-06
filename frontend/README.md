# AI Knowledge Assistant Frontend

## Local Development

1. **Start your backend** (make sure it's running on http://localhost:8000).
2. In this `frontend` directory, copy `.env.local.example` to `.env.local` (or create it if missing):
   ```sh
   cp .env.local.example .env.local
   ```
3. Set the backend URL in `.env.local`:
   ```env
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000/api/query
   ```
4. Start the Next.js dev server:
   ```sh
   npm run dev
   ```
5. Open [http://localhost:3000](http://localhost:3000) to use the chat UI.

## Vercel Deployment

1. Push your code to GitHub (or your Vercel-connected repo).
2. On Vercel, set the environment variable in your project settings:
   - `NEXT_PUBLIC_BACKEND_URL` = `https://<your-backend-domain>/api/query`
3. Deploy the project. Vercel will use the correct backend URL for production.

## Environment Variables
- `NEXT_PUBLIC_BACKEND_URL`: The full URL to your backend `/api/query` endpoint. Set this for both local and production as needed.

---

- The frontend will automatically use the correct backend URL based on the environment variable.
- If `NEXT_PUBLIC_BACKEND_URL` is not set, it defaults to `http://localhost:8000/api/query` for local development.
