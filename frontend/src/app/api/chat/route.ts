import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function POST(req: NextRequest) {
  const { query, top_k } = await req.json();
  const backendUrl = 'http://localhost:8000/api/query';

  const backendRes = await fetch(backendUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k }),
  });

  if (!backendRes.body) {
    return new Response('No response body from backend', { status: 500 });
  }

  // Stream the backend response directly to the client
  return new Response(backendRes.body, {
    status: backendRes.status,
    headers: {
      'Content-Type': backendRes.headers.get('Content-Type') || 'application/json',
    },
  });
}
