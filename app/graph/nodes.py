import json
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from app.llm.model import get_llm
from app.tools import load_tools

# Initialize tools and nodes once
TOOLS = load_tools()
TOOL_NODE = ToolNode(tools=TOOLS)

# LLM with tool binding
LLM = get_llm()
LLM_WITH_TOOLS = LLM.bind_tools(TOOLS)

def chatbot(state):
    """LLM node; returns the assistant message (possibly tool call)."""
    response = LLM_WITH_TOOLS.invoke(state["messages"])
    return {"messages": [response]}

def tool_node():
    """Return the ToolNode instance (used in builder)."""
    return TOOL_NODE

def route_from_llm():
    """Condition to decide whether to call tools based on LLM output."""
    return tools_condition
