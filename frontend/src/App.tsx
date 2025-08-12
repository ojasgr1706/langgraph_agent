import React, { useEffect, useMemo, useState } from 'react';
import './index.css';
import ThreadList from './components/ThreadList';
import ChatView from './components/ChatView';
import InputBar from './components/InputBar';
import { fetchThreads, fetchState, sendChat, deleteThread } from './api';
import type { ChatResponse, Message, ThreadMeta } from './types';

function newThreadId() {
  // client-side id; server will create state on first message
  return `t_${Date.now()}`;
}

export default function App() {
  const [threads, setThreads] = useState<ThreadMeta[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  // Load thread list on mount
  useEffect(() => {
    (async () => {
      try {
        const t = await fetchThreads();
        setThreads(t);
        if (!activeId && t.length > 0) setActiveId(t[0].thread_id);
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  // Load messages when activeId changes
  useEffect(() => {
    if (!activeId) return;
    setLoading(true);
    fetchState(activeId)
      .then((res: ChatResponse) => setMessages(res.messages || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [activeId]);

  async function handleSend(text: string) {
    if (!activeId) return;
    // Optimistic append of the user message
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    try {
      const res = await sendChat(activeId, text);
      setMessages(res.messages || []);
      // Refresh threads (titles/updated_at may change)
      fetchThreads().then(setThreads).catch(() => {});
    } catch (e) {
      console.error(e);
    }
  }

  function handleSelect(t: ThreadMeta) {
    setActiveId(t.thread_id);
  }

  function handleNew() {
    const id = newThreadId();
    // Optimistically add to UI with a placeholder title
    setThreads(prev => [{ thread_id: id, title: 'New chat' }, ...prev]);
    setActiveId(id);
    setMessages([]);
  }

  async function handleDelete(id: string) {
    try {
      await deleteThread(id);
      // Remove from local list
      setThreads(prev => prev.filter(t => t.thread_id !== id));
      // If we deleted the active one, clear the chat view
      if (activeId === id) {
        setActiveId(null);
        setMessages([]);
      }
    } catch (e) {
      console.error(e);
    }
  }

  const activeTitle = useMemo(() => {
    const t = threads.find(x => x.thread_id === activeId);
    return t?.title || activeId || 'Chat';
  }, [threads, activeId]);

  return (
    <div className="app">
      <ThreadList threads={threads} activeId={activeId} onSelect={handleSelect} onNew={handleNew} onDelete={handleDelete} />

      <main className="main">
        <div className="chat-header">
          <strong>{activeTitle}</strong>
          <div style={{ opacity: 0.6, fontSize: 12 }}>{activeId}</div>
        </div>

        <ChatView messages={messages} />
        <InputBar disabled={!activeId || loading} onSend={handleSend} />
      </main>
    </div>
  );
}