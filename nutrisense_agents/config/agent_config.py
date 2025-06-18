from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from nutrisense_agents.config.settings import settings

def get_chat_model(model_type: str, temperature: float = 0.7, streaming: bool = False):
    """
    Devuelve un modelo de chat basado en el tipo especificado.
    
    Args:
        model_type: Tipo de modelo ('gpt' o 'claude')
        temperature: Valor de temperatura para la generación (default: 0.7)
        
    Returns:
        Un modelo ChatOpenAI o ChatAnthropic
    """
    if model_type.lower() == "gpt":
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=temperature,
            max_retries=2,
            api_key=settings.OPENAI_API_KEY,
            streaming=streaming
        )
    elif model_type.lower() == "claude":
        return ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            temperature=temperature,
            streaming=streaming,
            timeout=None,
            max_retries=2,
            api_key=settings.ANTHROPIC_API_KEY
        )
    elif model_type.lower() == "groq":
        return ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=temperature,
            streaming=streaming,
            max_retries=2,
            api_key=settings.GROQ_API_KEY
        )
    else:
        raise ValueError(f"Tipo de modelo no soportado: {model_type}. Use 'gpt' o 'claude'.")