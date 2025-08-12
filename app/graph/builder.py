import os
from langgraph.graph import StateGraph, START
# from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mongodb import MongoDBSaver
from app.graph.state import State
from app.graph.nodes import chatbot, tool_node, route_from_llm

# Global variable to store the MongoDB saver context
_mongo_saver_context = None

def build_graph():
    global _mongo_saver_context
    
    # Use MongoDB saver for persistent memory
    DB_URI = "mongodb://localhost:27017"
    
    # Create MongoDB saver context and enter it
    # This keeps the connection open for the application lifecycle
    _mongo_saver_context = MongoDBSaver.from_conn_string(DB_URI)
    memory = _mongo_saver_context.__enter__()
    
    graph_builder = StateGraph(State)

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node())

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", route_from_llm())
    graph_builder.add_edge("tools", "chatbot")

    graph = graph_builder.compile(checkpointer=memory)
    return graph

def cleanup_mongo():
    """Clean up MongoDB connection when shutting down"""
    global _mongo_saver_context
    if _mongo_saver_context:
        _mongo_saver_context.__exit__(None, None, None)
        _mongo_saver_context = None
