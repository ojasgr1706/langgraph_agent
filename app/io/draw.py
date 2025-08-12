import os

def main():
    # Import here to avoid circular import
    from app.graph.builder import build_graph
    
    graph = build_graph()
    os.makedirs("images", exist_ok=True)
    with open("images/graph.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
    print("Wrote images/graph.png")

if __name__ == "__main__":
    main()
