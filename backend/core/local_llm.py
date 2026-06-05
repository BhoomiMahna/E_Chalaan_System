from langchain_community.llms import Ollama
from core.config import Config

def get_local_llm():
    """
    Get the local LLM instance.
    We use Ollama for hosting local models (e.g., Llama 3, Mistral).
    Ensure the Ollama server is running and the model is pulled: `ollama run <model_name>`
    """
    llm = Ollama(model=Config.LOCAL_LLM_MODEL)
    return llm
