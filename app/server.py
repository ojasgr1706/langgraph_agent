# app/server.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import json

from app.graph.builder import build_graph, cleanup_mongo
from app.threads.registry import delete_thread_by_id, list_threads, get_thread, touch_thread, delete_thread_by_id
from app.db.mongo import get_db

# ---------- App & CORS ----------
app = FastAPI(title="LangGraph Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite default
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Graph (single instance) ----------
graph = build_graph()

# ---------- Models ----------
class ChatRequest(BaseModel):
    thread_id: str
    user: str

class ChatResponse(BaseModel):
    thread_id: str
    messages: List[Dict[str, Any]]  # [{role, content, ...}]

# ---------- Utilities ----------
def _config_for(thread_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}

def _get_messages_for_thread(thread_id: str) -> List[Dict[str, Any]]:
    """
    Fetch LangGraph's message history for a given thread via the checkpointer,
    normalize roles, format tool messages, and SKIP empty contents.
    """
    try:
        state = graph.get_state(_config_for(thread_id))
        msgs = state.values.get("messages", [])
        norm = []

        def _is_nonempty_text(x) -> bool:
            # Treat only non-empty, non-whitespace strings as renderable.
            return isinstance(x, str) and x.strip() != ""

        for m in msgs:
            if hasattr(m, "type") and hasattr(m, "content"):
                role = getattr(m, "type", None)
                content = getattr(m, "content", None)
                name = getattr(m, "name", None) if hasattr(m, "name") else None

                # map roles
                if role == "ai":
                    role = "assistant"
                elif role == "human":
                    role = "user"

                # tool handling → "tool call: <query or raw>"
                if name:
                    role = "tool"
                    try:
                        parsed = json.loads(content) if isinstance(content, str) else content
                        if isinstance(parsed, dict) and "query" in parsed:
                            content = f"tool call: {parsed['query']}"
                        else:
                            content = f"tool call: {content}"
                    except Exception:
                        content = f"tool call: {content}"

                # SKIP empties
                if not _is_nonempty_text(content):
                    continue

                md = {"role": role, "content": content}
                if name:
                    md["name"] = name
                norm.append(md)

            elif isinstance(m, dict):
                role = m.get("role")
                content = m.get("content")

                # mark tools if name present, and add "tool call: ..."
                if "name" in m and m.get("name"):
                    role = "tool"
                    try:
                        parsed = json.loads(content) if isinstance(content, str) else content
                        if isinstance(parsed, dict) and "query" in parsed:
                            content = f"tool call: {parsed['query']}"
                        else:
                            content = f"tool call: {content}"
                    except Exception:
                        content = f"tool call: {content}"

                # SKIP empties
                if not _is_nonempty_text(content):
                    continue

                out = dict(m)
                out["role"] = role
                out["content"] = content
                norm.append(out)

            else:
                # fallback → skip if empty after str()
                text = str(m)
                if text.strip():
                    norm.append({"role": "unknown", "content": text})

        return norm

    except Exception:
        return []



# ---------- Routes ----------
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/threads")
def get_threads():
    """
    Returns: [{thread_id, title, created_at, updated_at, ...}] newest first
    """
    return list_threads()

@app.get("/state")
def get_state(thread_id: str = Query(..., description="Thread ID to fetch messages for")):
    """
    Return current message history for a given thread_id.
    """
    msgs = _get_messages_for_thread(thread_id)
    return ChatResponse(thread_id=thread_id, messages=msgs)

@app.post("/chat", response_model=ChatResponse)
def post_chat(req: ChatRequest):
    try:
        thread_id = str(req.thread_id)  # normalize to string everywhere
        # Ensure the thread exists and stays fresh in the sidebar:
        touch_thread(thread_id, req.user)

        config = {"configurable": {"thread_id": thread_id}}
        graph.invoke({"messages": [{"role": "user", "content": req.user}]}, config)

        msgs = _get_messages_for_thread(thread_id)
        return ChatResponse(thread_id=thread_id, messages=msgs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/threads/{thread_id}")
def delete_thread(thread_id: str):
    
    deleted = delete_thread_by_id(thread_id)

    # If you want to signal nonexistence:
    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Keep it simple: always 204
    return {"ok": True}

# ---------- Lifespan ----------
@app.on_event("shutdown")
def on_shutdown():
    cleanup_mongo()
