# Modulus — LangGraph Agent (Web Search + Math module)

A conversational AI agent built with LangGraph that combines web search (Tavily) and calculator tools with an LLM for intelligent task execution.

![Frontend Interface](images/app_image.png)

## Setup
1) `python -m venv .venv && source .venv/bin/activate`
2) `pip install -r requirements.txt`
3) Copy `.env.example` to `.env` and set your keys (OPENAI_API_KEY, TAVILY_API_KEY, OPENAI_MODEL)
4) Ensure MongoDB is running locally on `localhost:27017` (for persistent conversation memory)
5) For browser version: `cd frontend && npm install`

## Run

### CLI Version (Terminal-based)
- **Chat interface**: `python -m app.cli.chat`
- **Draw graph PNG**: `python -m app.io.draw`

### Browser Version (Web Interface)

**Terminal 1 - Backend Server:**
```bash
uvicorn app.server:app --reload
```
Backend runs on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:5173`

Open `http://localhost:5173` in your browser to access the web interface.

## Architecture

### Backend & Agent Orchestration

The system uses **LangGraph** to orchestrate a stateful agent workflow:

- **StateGraph Architecture**: Built on LangGraph's `StateGraph` with two primary nodes:
  - **Chatbot Node**: LLM (OpenAI) that processes user messages and decides whether to use tools
  - **Tools Node**: Executes tool calls (TavilySearch for web search, Calculator for math operations)

- **Conditional Routing**: The agent uses `tools_condition` to automatically route between the chatbot and tools nodes based on LLM output. If the LLM decides tools are needed, execution flows to the tools node, then back to the chatbot for a final response.

- **Persistent Memory**: Uses MongoDB checkpointing (`MongoDBSaver`) to maintain conversation history across sessions. Each conversation thread has a unique `thread_id` and maintains full message history.

- **Streaming**: The FastAPI backend supports Server-Sent Events (SSE) for real-time streaming of:
  - Assistant token deltas (partial responses)
  - Tool call outputs
  - Completion events

- **Tools Available**:
  - **TavilySearch**: Web search with configurable result limits
  - **Calculator**: Safe evaluation of mathematical expressions

- **API Endpoints**: RESTful API for thread management, chat streaming, and state retrieval. CORS configured for frontend communication.

### Frontend

Simple React + TypeScript interface built with Vite. Provides a chat UI with thread management, real-time message streaming, and conversation history.

## Notes
- Uses TavilySearch via `langchain_tavily` and an LLM via `langchain-openai`.
- Streams tokens and tool outputs, formatted using `rich` in CLI mode.
- More features like OCR, calendar and file io planned.
