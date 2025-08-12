from langchain_tavily import TavilySearch

def get_tavily_tool():
    # TavilySearch is a LangChain tool compatible with ToolNode
    # You can pass max_results, include_answer, etc.
    return TavilySearch(max_results=2)
