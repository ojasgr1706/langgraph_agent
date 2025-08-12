import React, { useEffect, useRef } from 'react';
import type { Message } from '../types';

interface Props {
  messages: Message[];
}

export default function ChatView({ messages }: Props) {
  const endRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  function formatContent(m: Message) {
    if (m.role === 'tool') {
      try {
        const parsed = typeof m.content === 'string' ? JSON.parse(m.content) : m.content;
        if (parsed && typeof parsed.query === 'string') {
          return parsed.query;
        }
      } catch (e) {
        // If not valid JSON, fall back
      }
    }
    return m.content;
  }

  return (
    <div className="messages">
      {messages.map((m, i) => (
        <div key={i} className={`msg ${m.role}`}>
          {formatContent(m)}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}