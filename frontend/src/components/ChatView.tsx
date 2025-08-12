import React, { useEffect, useRef } from 'react';
import type { Message } from '../types';

interface Props {
  messages: Message[];
}

export default function ChatView({ messages }: Props) {
  const endRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  return (
    <div className="messages">
      {messages.map((m, i) => (
        <div key={i} className={`msg ${m.role}`}>
          {m.content}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}