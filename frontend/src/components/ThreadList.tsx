import React from 'react';
import type { ThreadMeta } from '../types';

interface Props {
  threads: ThreadMeta[];
  activeId: string | null;
  onSelect: (t: ThreadMeta) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export default function ThreadList({ threads, activeId, onSelect, onNew, onDelete }: Props) {
  return (
    <aside className="sidebar">
      <header>
        <strong>Chats</strong>
        <button onClick={onNew} title="New chat">+ New</button>
      </header>
      <ul className="thread-list">
        {threads.map(t => (
          <li key={t.thread_id} className={`thread-item ${activeId === t.thread_id ? 'active' : ''}`}>
            <div onClick={() => onSelect(t)} style={{ flex: 1, cursor: 'pointer' }}>
              <div className="thread-title">{t.title || t.thread_id}</div>
              <div className="thread-sub">{t.updated_at ? new Date(t.updated_at).toLocaleString() : ''}</div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation(); // prevents selecting the row
                if (window.confirm('Are you sure you want to delete this chat?')) {
                  onDelete(t.thread_id);
                }
              }}
              className="delete-btn"
              title="Delete chat"
            >
              🗑️
            </button>
          </li>
        ))}
        {threads.length === 0 && (
          <li className="thread-item">
            <div className="thread-sub">No threads yet</div>
          </li>
        )}
      </ul>
    </aside>
  );
}