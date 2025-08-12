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

export type StreamEvent =
  | { event: 'delta'; data: { role: 'assistant'; content: string } }
  | { event: 'tool'; data: { role: 'tool'; name?: string; content: string } }
  | { event: 'done'; data: any }
  | { event: 'error'; data: { message: string } };

export async function* streamChat(threadId: string, user: string): AsyncGenerator<StreamEvent> {
  const url = `${API}/chat/stream?thread_id=${encodeURIComponent(threadId)}&user=${encodeURIComponent(user)}`;
  const res = await fetch(url, {
    method: 'GET',
    headers: { Accept: 'text/event-stream' },
  });
  if (!res.ok || !res.body) throw new Error(`stream: ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE messages are separated by \n\n
    let splitIndex: number;
    while ((splitIndex = buffer.indexOf('\n\n')) !== -1) {
      const raw = buffer.slice(0, splitIndex);
      buffer = buffer.slice(splitIndex + 2);

      // Parse single SSE block: multiple lines like "event: X" / "data: Y"
      let event: string | undefined;
      let dataLine = '';
      for (const line of raw.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim();
        else if (line.startsWith('data:')) dataLine += line.slice(5).trim();
      }
      if (!event) continue;
      try {
        const data = dataLine ? JSON.parse(dataLine) : {};
        yield { event, data } as StreamEvent;
      } catch {
        // ignore parse errors
      }
    }
  }
}