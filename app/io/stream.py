import json
from typing import Iterable, Tuple
from rich.console import Console
from rich.markdown import Markdown
from app.threads.registry import upsert_thread
from app.db.mongo import get_db

console = Console()

def stream_graph(graph, user_input: str, config: dict = {"configurable": {"thread_id": 1}}):    
    thread_id = config["configurable"]["thread_id"]

    # Only insert if thread_id doesn't exist
    if not get_db()["threads"].find_one({"thread_id": thread_id}):
        upsert_thread(thread_id, user_input)

    console.print("[bold cyan]Assistant:[/bold cyan] ", end="")
    for token, meta in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="messages",
    ):
        node = meta.get("langgraph_node")
        # Tool outputs
        if node == "tools":
            try:
                content = token.content
                # Tool messages are typically structured as a JSON dict in .content
                data = json.loads(content) if isinstance(content, str) else content
                name = token.name or "tool"
                # Tavily returns results; calculator returns a string
                if isinstance(data, dict) and "results" in data:
                    title = data["results"][0].get("title", "result")
                    console.print(f"\n[bold yellow][TOOL:{name}][/bold yellow] {title}")
                else:
                    console.print(f"\n[bold yellow][TOOL:{name}][/bold yellow] {data}")
            except Exception:
                console.print(f"\n[bold yellow][TOOL][/bold yellow] {token.content}")
        else:
            # LLM tokens (delta chunks)
            text = token.content or ""
            console.print(text, end="")
    console.print()  # newline
    
    # for state in graph.get_state_history(config):
    #     print(state)
    #     print("----------------------------------------")
    #     print("Num Messages: ", len(state.values["messages"]), "Next: ", state.next)
    #     print()
