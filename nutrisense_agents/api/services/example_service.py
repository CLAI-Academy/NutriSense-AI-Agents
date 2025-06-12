from nutrisense_agents.ai_companion.agents.example_agent import get_example_agent_chain

chain = get_example_agent_chain()

def get_example_service(user: str, preferences: str, allergies: str):
    return chain.invoke({
        "user": user,
        "preferences": preferences,
        "allergies": allergies
    })



if __name__ == "__main__":
    print(get_example_service(user="Juan", preferences="Vegetariano", allergies="Gluten"))