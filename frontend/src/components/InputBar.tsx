import React, { useState } from 'react';

interface Props {
  disabled?: boolean;
  onSend: (text: string) => Promise<void> | void;
}

export default function InputBar({ disabled, onSend }: Props) {
  const [text, setText] = useState('');
  const [sending, setSending] = useState(false);

  async function handleSend() {
    const trimmed = text.trim();
    if (!trimmed || sending || disabled) return;
    setSending(true);
    try {
      await onSend(trimmed);
      setText('');
    } finally {
      setSending(false);
    }
  }

  function onKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="input-bar">
      <input
        placeholder="Ask anything…"
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={onKey}
        disabled={disabled || sending}
      />
      <button onClick={handleSend} disabled={disabled || sending} title="Send">
        →
      </button>
    </div>
  );
}