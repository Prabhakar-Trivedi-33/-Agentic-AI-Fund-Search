from typing import Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage
from .config import settings

def create_llm(temperature: float = 0.1, streaming: bool = False, callbacks: Optional[list] = None) -> ChatOpenAI:
    """
    Create and configure a ChatOpenAI instance.
    
    Args:
        temperature: Creativity level of the model (0.0 to 2.0)
        streaming: Whether to stream responses
        callbacks: Optional callbacks for streaming
        
    Returns:
        ChatOpenAI: Configured LLM instance
    """
    return ChatOpenAI(
        model="gpt-4-turbo",
        temperature=temperature,
        api_key=settings.openai_api_key,
        streaming=streaming,
        callbacks=callbacks,
        verbose=settings.app_env == "development"
    )

async def generate_response(messages: list[BaseMessage], temperature: float = 0.1) -> str:
    """
    Generate a response from the LLM.
    
    Args:
        messages: List of conversation messages
        temperature: Creativity level of the model
        
    Returns:
        str: Generated response
    """
    llm = create_llm(temperature=temperature)
    response = await llm.agenerate([messages])
    return response.generations[0][0].text