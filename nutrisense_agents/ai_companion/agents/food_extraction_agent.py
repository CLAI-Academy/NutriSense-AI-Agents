from langchain_core.prompts import ChatPromptTemplate
from nutrisense_agents.ai_companion.schemas.food_analysis_schema import ImageAnalysisResult, NutritionalCompatibility
from nutrisense_agents.config.agent_config import get_chat_model
from nutrisense_agents.ai_companion.prompts.food_analysis_prompt import IMG_ANALISIS_PROMPT, TEXT_ANALYSIS_PROMPT, COMPATIBILITY_ANALYSIS_PROMPT

def get_image_extraction_agent_chain():
    """Cadena específica para extracción de ingredientes desde imágenes"""
    model = get_chat_model(model_type="gpt", temperature=0.3).with_structured_output(ImageAnalysisResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", IMG_ANALISIS_PROMPT),
        ("human", [
            {"type": "text", "text": "Notas adicionales: {notes}"},
            {"type": "image_url", "image_url": {"url": "{image_url}"}}
        ])
    ])

    chain = prompt | model
    return chain

def get_text_extraction_agent_chain():
    """Cadena específica para extracción de ingredientes desde texto"""
    model = get_chat_model(model_type="gpt", temperature=0.3).with_structured_output(ImageAnalysisResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", TEXT_ANALYSIS_PROMPT),
        ("human", "Texto a analizar: {text_description}")
    ])

    chain = prompt | model
    return chain

def get_compatibility_agent_chain():
    """Cadena específica para análisis de compatibilidad nutricional"""
    model = get_chat_model(model_type="gpt", temperature=0.1).with_structured_output(NutritionalCompatibility)

    prompt = ChatPromptTemplate.from_messages([
        ("system", COMPATIBILITY_ANALYSIS_PROMPT),
        ("human", "Analiza la compatibilidad de esta comida con los objetivos del usuario.")
    ])

    chain = prompt | model
    return chain