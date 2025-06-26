from langchain_core.prompts import ChatPromptTemplate

from nutrisense_agents.ai_companion.schemas.img_analysis_schema import ImageAnalysisResult

from nutrisense_agents.config.agent_config import get_chat_model

from nutrisense_agents.ai_companion.prompts.text_analysis_prompt import TEXT_ANALYSIS_PROMPT

def get_text_extraction_agent_chain():
    model = get_chat_model(model_type="gpt", temperature=0.3).with_structured_output(ImageAnalysisResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", TEXT_ANALYSIS_PROMPT),
        ("human", "Texto a analizar: {text_description}")
    ])

    chain = prompt | model

    return chain