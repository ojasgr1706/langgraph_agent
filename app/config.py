import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not set. Put it in .env")

if not TAVILY_API_KEY:
    raise EnvironmentError("TAVILY_API_KEY not set. Put it in .env")
