from langchain.chat_models import init_chat_model
from app.config import OPENAI_MODEL

# Single place to init and bind tools later
def get_llm():
    # e.g. "openai:gpt-4o-mini"
    return init_chat_model(f"openai:{OPENAI_MODEL}")
