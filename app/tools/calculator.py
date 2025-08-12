from langchain.tools import tool

@tool("calculator", return_direct=False)
def calculator(expression: str) -> str:
    """Evaluate a basic math expression, e.g., '12 * (3 + 4) - 2'."""
    try:
        # Restricted eval
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"
