from langchain_core.prompts import ChatPromptTemplate
from typing import List

from nutrisense_agents.ai_companion.schemas.macronutrient_schema import MacronutrientExtraction
from nutrisense_agents.config.agent_config import get_chat_model
from nutrisense_agents.ai_companion.prompts.macronutrient_prompt import MACRONUTRIENT_EXTRACTION_PROMPT

def get_macronutrient_extraction_chain():
    """
    Crea una cadena de procesamiento para extraer macronutrientes de ingredientes.
    
    Returns:
        Chain configurado para extraer información nutricional
    """
    model = get_chat_model(model_type="gpt", temperature=0.1).with_structured_output(MacronutrientExtraction)

    prompt = ChatPromptTemplate([
        ("system", MACRONUTRIENT_EXTRACTION_PROMPT),
        ("human", """
        Lista de ingredientes a analizar: {ingredients}
        
        Contexto adicional:
        - Tipo de comida: {meal_type}
        - Método de preparación: {preparation_method}
        - Cantidad aproximada de la porción: {portion_size}
        - Notas adicionales: {additional_notes}
        
        Por favor, analiza cada ingrediente y proporciona la información nutricional solicitada.
        """)
    ])

    chain = prompt | model
    return chain

def process_multiple_ingredients(ingredients: List[str], meal_type: str = "unknown", 
                               preparation_method: str = "unknown", 
                               portion_size: str = "porción estándar",
                               additional_notes: str = ""):
    """
    Procesa múltiples ingredientes y devuelve una lista de extracciones de macronutrientes.
    
    Args:
        ingredients: Lista de ingredientes a procesar
        meal_type: Tipo de comida (desayuno, almuerzo, cena, snack)
        preparation_method: Método de preparación
        portion_size: Tamaño de la porción
        additional_notes: Notas adicionales
        
    Returns:
        Lista de MacronutrientExtraction para cada ingrediente
    """
    chain = get_macronutrient_extraction_chain()
    results = []
    
    for ingredient in ingredients:
        try:
            result = chain.invoke({
                "ingredients": [ingredient],  # Procesar uno a la vez para mayor precisión
                "meal_type": meal_type,
                "preparation_method": preparation_method,
                "portion_size": portion_size,
                "additional_notes": additional_notes
            })
            results.append(result)
        except Exception as e:
            # Log del error y continuar con el siguiente ingrediente
            print(f"Error procesando ingrediente {ingredient}: {str(e)}")
            continue
    
    return results
