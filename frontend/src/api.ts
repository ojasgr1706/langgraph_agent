import type { ChatResponse, ThreadMeta } from './types';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function createThread(title?: string) {
  const res = await fetch(`${API}/threads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`createThread: ${res.status}`);
  return res.json(); // { thread_id, title, created_at, updated_at, ... }
}

export async function fetchThreads(): Promise<ThreadMeta[]> {
  const res = await fetch(`${API}/threads`);
  if (!res.ok) throw new Error(`threads: ${res.status}`);
  return res.json();
}

export async function fetchState(threadId: string): Promise<ChatResponse> {
  const res = await fetch(`${API}/state?thread_id=${encodeURIComponent(threadId)}`);
  if (!res.ok) throw new Error(`state: ${res.status}`);
  return res.json();
}

export async function sendChat(threadId: string, userText: string): Promise<ChatResponse> {
  const res = await fetch(`${API}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thread_id: threadId, user: userText })
  });
  if (!res.ok) throw new Error(`chat: ${res.status}`);
  return res.json();
}

export async function deleteThread(threadId: string): Promise<void> {
  const res = await fetch(`${API}/threads/${encodeURIComponent(threadId)}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`delete: ${res.status}`);
}