from langchain_core.prompts import ChatPromptTemplate

from nutrisense_agents.ai_companion.schemas.img_analysis_schema import ImageAnalysisResult

from nutrisense_agents.config.agent_config import get_chat_model

from nutrisense_agents.ai_companion.prompts.img_analisis_prompt import IMG_ANALISIS_PROMPT

def get_image_extraction_agent_chain():
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
