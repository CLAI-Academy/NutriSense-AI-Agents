from langchain_core.prompts import ChatPromptTemplate

from nutrisense_agents.ai_companion.schemas.example_schema import ExampleAgent

from nutrisense_agents.config.agent_config import get_chat_model

from nutrisense_agents.ai_companion.prompts.example_prompt import EXAMPLE_PROMPT

def get_example_agent_chain():
    model = get_chat_model(model_type="gpt", temperature=0.3).with_structured_output(ExampleAgent)

    prompt = ChatPromptTemplate([
            ("system",EXAMPLE_PROMPT),
            ("human", " user: {user}, preferences: {preferences}, allergies: {allergies} ")
            ])

    chain = prompt | model

    return chain
