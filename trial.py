# # imports
# import os
# import json
# from typing import Annotated
# from typing_extensions import TypedDict
# from IPython.display import Image, display

# from app.llm.model import get_llm
# from app.tools import load_tools
# from app.graph.builder import build_graph

# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langgraph.prebuilt import ToolNode, tools_condition
# from langgraph.checkpoint.memory import InMemorySaver

# from dotenv import load_dotenv

# # load environment variables
# load_dotenv()

# if "OPENAI_API_KEY" not in os.environ:
# 	raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

# # define state
# class State(TypedDict):
# 	messages: Annotated[list, "add_messages"]

# # initialize tools and graph
# tools = load_tools()
# graph = build_graph()

# # initialize llm
# llm = get_llm()
# llm_with_tools = llm.bind_tools(tools)

# def chatbot(state: State):
# 	return {"messages": [llm_with_tools.invoke(state["messages"])]}

# # initialize memory
# memory = InMemorySaver()

# # build graph
# graph_builder = StateGraph(State)

# graph_builder.add_node("tools", ToolNode(tools=tools))
# graph_builder.add_node("chatbot", chatbot)

# graph_builder.add_edge(START, "chatbot")
# graph_builder.add_conditional_edges(
# 	"chatbot",
# 	tools_condition,
# )
# graph_builder.add_edge("tools", "chatbot")
# graph = graph_builder.compile(checkpointer=memory)

# # draw graph
# def draw_graph():
# 	os.makedirs("images", exist_ok=True)
# 	with open("images/graph.png", "wb") as f:
# 		f.write(graph.get_graph().draw_mermaid_png())

# # stream graph updates
# def stream_graph_updates(user_input: str):
# 		print("Assistant: ", end="")
# 		meta = []
# 		tokens = []
# 		for token, metadata in graph.stream(
# 			{"messages": [{"role": "user", "content": user_input}]},
# 			{"configurable" : {"thread_id" : "1"}},
# 			stream_mode = "messages"):
			
# 			if metadata.get("langgraph_node") == "tools":
# 				content = json.loads(token.content)
# 				print("[TOOL OUTPUT] ", end="", flush=True)
# 				print(f"[{token.name}] {content.get('results')[0].get('title')}", flush=True)
# 				print()
# 			else:
# 				print(token.content, end="", flush=True)
# 			meta.append(metadata)
# 			tokens.append(token)

# 		print()

# # run loop
# def run_loop():
# 	while True:
# 		user_input = input("User: ")
# 		if user_input.lower() in ["quit", "exit", "q"]:
# 			break
# 		stream_graph_updates(user_input)


# if __name__ == "__main__":
# 	draw_graph()
# 	run_loop()

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
print(client.list_database_names())
