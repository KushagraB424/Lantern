import os
from typing import Any, List, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.embeddings import Embeddings
from pydantic import SecretStr

load_dotenv()

class DummyLLM(BaseChatModel):
    """A dummy LLM returned when API keys are missing to prevent application crashes."""
    
    @property
    def _llm_type(self) -> str:
        return "dummy"
        
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> ChatResult:
        msg = AIMessage(content="[LLM API Key missing] This is a dummy response. Please provide the required API keys in the backend .env file to enable actual AI functionality.")
        return ChatResult(generations=[ChatGeneration(message=msg)])

def get_llm(provider: str, model_name: str, temperature: float = 0.0, max_tokens: int = 1000) -> BaseChatModel:
    """
    Factory function to get an LLM instance based on the provider and settings.
    """
    provider = provider.lower()
    
    if provider == "google" or "gemini" in model_name.lower():
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_google_api_key_here":
            return DummyLLM()
            
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_tokens,
            api_key=SecretStr(api_key)
        )
        
    elif provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key == "your_openrouter_api_key_here":
            return DummyLLM()
            
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=SecretStr(api_key),
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Lantern SaaS"
            }
        )
        
    raise ValueError(f"Unsupported LLM provider: {provider}")

class DummyEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.0]*768 for _ in texts]
    def embed_query(self, text):
        return [0.0]*768

def get_embeddings(provider: str = "google", model_name: str = "models/text-embedding-004") -> Embeddings:
    if provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and api_key != "placeholder_key":
            try:
                return GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=api_key)
            except Exception as e:
                print(f"Error initializing Google Embeddings: {e}")
                return DummyEmbeddings()
        else:
            return DummyEmbeddings()
    else:
        return DummyEmbeddings()
