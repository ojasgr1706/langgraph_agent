from app.tools.calculator import calculator
from app.tools.tavily_search import get_tavily_tool

def load_tools():
    # Return a list of LC tools
    tavily = get_tavily_tool()
    return [tavily, calculator]
