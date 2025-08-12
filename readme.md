# Modulus — LangGraph Agent (Tavily + Calculator)

## Setup
1) `python -m venv .venv && source .venv/bin/activate`
2) `pip install -r requirements.txt`
3) Copy `.env.example` to `.env` and set your keys.

## Run
- Chat (recommended): `python -m app.cli.chat`
- Draw graph PNG: `python -m app.io.draw`

## Notes
- Uses TavilySearch via `langchain_tavily` and an LLM via `langchain-openai`.
- Streams tokens and tool outputs; nicely formatted via `rich`.
