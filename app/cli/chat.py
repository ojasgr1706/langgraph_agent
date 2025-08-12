from app.graph.builder import build_graph, cleanup_mongo
from app.io.stream import stream_graph
from rich.console import Console
from app.threads.registry import delete_all_threads, delete_thread_by_id, list_threads
# from app.session.session import Session

console = Console()

def main():
    thread_id = 1
    Session = dict()
    config = {"configurable": {"thread_id": thread_id}}

    graph = build_graph()
    console.print("[bold green]LangGraph agent ready.[/bold green] Type 'exit' to quit.")
    
    try:
        while True:
            user = input("User > ").strip()
            if user.lower() in {"exit", "quit", "q"}:
                console.print("[bold]QUIT[/bold]")
                break
            elif user.lower() == "change thread":
                thread_id = input("Enter new thread_id: ")
                config = {"configurable": {"thread_id": thread_id}}
                continue
            elif user.lower() == "all threads":
                # Get all threads
                threads = list_threads()
                # Print thread information
                for thread in threads:
                    print(f"ID: {thread['thread_id']}, Title: {thread['title']}")
                continue
            elif user.lower() == "delete all":
                delete_all_threads()
                thread_id = 1
                continue

            elif user.lower() == "delete thread":
                thread_del = input("thread_id to delete: ")
                delete_thread_by_id(thread_del)
                continue

            stream_graph(graph, user, config)

            # state = graph.get_state(config)
            # graph.update_state(config, {})
            # if not session.thread_exists(thread_id):
            # print({k: v for k, v in state.values.items() if k in ("threads")})
    finally:
        # Clean up MongoDB connection
        cleanup_mongo()

if __name__ == "__main__":
    main()
