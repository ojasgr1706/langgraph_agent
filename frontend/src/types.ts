export type Role = 'user' | 'assistant' | 'system' | string;

export interface Message {
  role: Role;
  content: string;
  name?: string;
}

export interface ThreadMeta {
  thread_id: string;
  title: string;
  created_at?: string;
  updated_at?: string;
}

export interface ChatResponse {
  thread_id: string;
  messages: Message[];
}