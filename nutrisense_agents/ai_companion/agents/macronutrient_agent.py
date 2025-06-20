from langchain_core.prompts import ChatPromptTemplate
from typing import List
from datetime import datetime

from nutrisense_agents.ai_companion.schemas.macronutrient_schema import (
    MacronutrientExtraction, 
    ContextualizedMacronutrientExtraction,
    UserNutritionalProfile,
    NutritionalCalculations,
    ContextualizedAnalysis,
    Gender,
    ActivityLevel,
    Goal
)
from nutrisense_agents.config.agent_config import get_chat_model
from nutrisense_agents.ai_companion.prompts.macronutrient_prompt import (
    MACRONUTRIENT_EXTRACTION_PROMPT, 
    CONTEXTUALIZED_MACRONUTRIENT_PROMPT
)

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
        
        Por favor, analiza cada ingrediente y proporciona la información nutricional solicitada.
        """)
    ])

    chain = prompt | model
    return chain

# def process_multiple_ingredients(ingredients: List[str], meal_type: str = "unknown", 
#                                preparation_method: str = "unknown", 
#                                portion_size: str = "porción estándar",
#                                additional_notes: str = ""):
#     """
#     Procesa múltiples ingredientes y devuelve una lista de extracciones de macronutrientes.
    
#     Args:
#         ingredients: Lista de ingredientes a procesar
#         meal_type: Tipo de comida (desayuno, almuerzo, cena, snack)
#         preparation_method: Método de preparación
#         portion_size: Tamaño de la porción
#         additional_notes: Notas adicionales
        
#     Returns:
#         Lista de MacronutrientExtraction para cada ingrediente
#     """
#     chain = get_macronutrient_extraction_chain()
#     results = []
    
#     for ingredient in ingredients:
#         try:
#             result = chain.invoke({
#                 "ingredients": [ingredient],  # Procesar uno a la vez para mayor precisión
#                 "meal_type": meal_type,
#                 "preparation_method": preparation_method,
#                 "portion_size": portion_size,
#                 "additional_notes": additional_notes
#             })
#             results.append(result)
#         except Exception as e:
#             # Log del error y continuar con el siguiente ingrediente
#             print(f"Error procesando ingrediente {ingredient}: {str(e)}")
#             continue
    
#     return results

# def calculate_nutritional_targets(user_profile: UserNutritionalProfile) -> NutritionalCalculations:
#     """
#     Calculate nutritional targets based on user profile using scientific formulas.
    
#     Args:
#         user_profile: User's nutritional profile
        
#     Returns:
#         NutritionalCalculations with all target values
#     """
#     # 1. Calculate ideal weight using Lorentz formula
#     if user_profile.gender == Gender.MALE:
#         ideal_weight = (user_profile.height_cm - 100) - ((user_profile.height_cm - 150) / 4)
#     else:  # FEMALE
#         ideal_weight = (user_profile.height_cm - 100) - ((user_profile.height_cm - 150) / 2.5)
    
#     weight_difference = user_profile.weight_kg - ideal_weight
    
#     # 2. Calculate BMR using Harris-Benedict revised formula
#     if user_profile.gender == Gender.MALE:
#         bmr = 88.362 + (13.397 * user_profile.weight_kg) + (4.799 * user_profile.height_cm) - (5.677 * user_profile.age)
#     else:  # FEMALE
#         bmr = 447.593 + (9.247 * user_profile.weight_kg) + (3.098 * user_profile.height_cm) - (4.330 * user_profile.age)
    
#     # 3. Calculate VCT (Total Daily Energy Expenditure)
#     activity_factors = {
#         ActivityLevel.SEDENTARY: 1.2,
#         ActivityLevel.LIGHTLY_ACTIVE: 1.375,
#         ActivityLevel.MODERATELY_ACTIVE: 1.55,
#         ActivityLevel.VERY_ACTIVE: 1.725,
#         ActivityLevel.EXTRA_ACTIVE: 1.9
#     }
    
#     vct = bmr * activity_factors[user_profile.activity_level]
    
#     # 4. Calculate macro distribution based on goal
#     macro_distributions = {
#         Goal.WEIGHT_LOSS: {"protein": 0.325, "fat": 0.275, "carbs": 0.40},
#         Goal.MUSCLE_GAIN: {"protein": 0.275, "fat": 0.225, "carbs": 0.50},
#         Goal.MAINTENANCE: {"protein": 0.225, "fat": 0.275, "carbs": 0.50},
#         Goal.ENDURANCE: {"protein": 0.175, "fat": 0.225, "carbs": 0.60},
#         Goal.STRENGTH: {"protein": 0.275, "fat": 0.275, "carbs": 0.45}
#     }
    
#     distribution = macro_distributions[user_profile.goal]
    
#     # Calculate target macros in grams
#     target_protein_g = (vct * distribution["protein"]) / 4  # 4 cal/g protein
#     target_carbs_g = (vct * distribution["carbs"]) / 4      # 4 cal/g carbs
#     target_fat_g = (vct * distribution["fat"]) / 9          # 9 cal/g fat
    
#     return NutritionalCalculations(
#         ideal_weight_kg=round(ideal_weight, 1),
#         weight_difference_kg=round(weight_difference, 1),
#         bmr_calories=round(bmr, 0),
#         vct_calories=round(vct, 0),
#         target_protein_g=round(target_protein_g, 1),
#         target_carbs_g=round(target_carbs_g, 1),
#         target_fat_g=round(target_fat_g, 1),
#         protein_percentage=round(distribution["protein"] * 100, 1),
#         carbs_percentage=round(distribution["carbs"] * 100, 1),
#         fat_percentage=round(distribution["fat"] * 100, 1)
#     )

# def get_contextualized_macronutrient_chain():
#     """
#     Create a chain for contextualized macronutrient analysis.
    
#     Returns:
#         Chain configured for contextualized nutritional analysis
#     """
#     model = get_chat_model(model_type="gpt", temperature=0.1).with_structured_output(ContextualizedAnalysis)

#     prompt = ChatPromptTemplate([
#         ("system", CONTEXTUALIZED_MACRONUTRIENT_PROMPT),
#         ("human", """
#         INFORMACIÓN DEL ALIMENTO CONSUMIDO:
#         {food_data}
        
#         PERFIL NUTRICIONAL DEL USUARIO:
#         {user_profile}
        
#         OBJETIVOS NUTRICIONALES CALCULADOS:
#         {nutritional_targets}
        
#         Por favor, realiza un análisis nutricional contextualizado completo que incluya:
#         1. Todos los cálculos científicos requeridos
#         2. Porcentaje de objetivos diarios cubiertos
#         3. Puntuación de alineación con objetivos (0-10)
#         4. Recomendaciones personalizadas
#         5. Advertencias si es necesario
#         6. Insights específicos según el objetivo del usuario
#         """)
#     ])

#     chain = prompt | model
#     return chain

# def analyze_food_with_context(
#     food_extraction: MacronutrientExtraction,
#     user_profile: UserNutritionalProfile,
#     mode: str = "local"
# ) -> ContextualizedMacronutrientExtraction:
#     """
#     Analyze food intake in the context of user's nutritional profile and goals.
    
#     Args:
#         food_extraction: Basic macronutrient extraction
#         user_profile: User's nutritional profile
#         mode: Analysis mode ("local" or "full")
        
#     Returns:
#         ContextualizedMacronutrientExtraction with complete analysis
#     """
#     # Calculate nutritional targets
#     nutritional_calculations = calculate_nutritional_targets(user_profile)
    
#     # Prepare data for the LLM chain
#     food_data = {
#         "name": food_extraction.name,
#         "total_calories": food_extraction.total_calories,
#         "total_protein": food_extraction.total_protein,
#         "total_carbs": food_extraction.total_carbs,
#         "total_fat": food_extraction.total_fat,
#         "estimated_quantity_grams": food_extraction.estimated_quantity_grams,
#         "category": food_extraction.category,
#         "preparation_method": food_extraction.preparation_method
#     }
    
#     profile_data = {
#         "age": user_profile.age,
#         "gender": user_profile.gender.value,
#         "weight_kg": user_profile.weight_kg,
#         "height_cm": user_profile.height_cm,
#         "activity_level": user_profile.activity_level.value,
#         "goal": user_profile.goal.value,
#         "dietary_restrictions": user_profile.dietary_restrictions,
#         "medical_conditions": user_profile.medical_conditions
#     }
    
#     targets_data = {
#         "ideal_weight_kg": nutritional_calculations.ideal_weight_kg,
#         "bmr_calories": nutritional_calculations.bmr_calories,
#         "vct_calories": nutritional_calculations.vct_calories,
#         "target_protein_g": nutritional_calculations.target_protein_g,
#         "target_carbs_g": nutritional_calculations.target_carbs_g,
#         "target_fat_g": nutritional_calculations.target_fat_g
#     }
    
#     # Get contextualized analysis from LLM
#     chain = get_contextualized_macronutrient_chain()
    
#     try:
#         contextualized_analysis = chain.invoke({
#             "food_data": str(food_data),
#             "user_profile": str(profile_data),
#             "nutritional_targets": str(targets_data)
#         })
#     except Exception as e:
#         # Fallback to basic analysis if LLM fails
#         contextualized_analysis = ContextualizedAnalysis(
#             calories_vs_target_percent=round((food_extraction.total_calories / nutritional_calculations.vct_calories) * 100, 1),
#             protein_vs_target_percent=round((food_extraction.total_protein / nutritional_calculations.target_protein_g) * 100, 1),
#             carbs_vs_target_percent=round((food_extraction.total_carbs / nutritional_calculations.target_carbs_g) * 100, 1),
#             fat_vs_target_percent=round((food_extraction.total_fat / nutritional_calculations.target_fat_g) * 100, 1),
#             alignment_score=5.0,  # Neutral score on error
#             recommendations=["Error en análisis contextualizado, consulte a un profesional"],
#             warnings=None,
#             goal_specific_notes="Análisis básico por error en procesamiento"
#         )
    
#     return ContextualizedMacronutrientExtraction(
#         food_extraction=food_extraction,
#         user_profile=user_profile,
#         nutritional_calculations=nutritional_calculations,
#         contextualized_analysis=contextualized_analysis,
#         analysis_timestamp=datetime.now(),
#         mode=mode
#     )

# def get_basic_macronutrient_analysis(
#     ingredients: List[str], 
#     meal_type: str = "unknown",
#     preparation_method: str = "unknown", 
#     portion_size: str = "porción estándar",
#     additional_notes: str = ""
# ) -> MacronutrientExtraction:
#     """
#     Get basic macronutrient analysis for a single ingredient or combined meal.
    
#     Args:
#         ingredients: List of ingredients to analyze
#         meal_type: Type of meal
#         preparation_method: Preparation method
#         portion_size: Portion size
#         additional_notes: Additional notes
        
#     Returns:
#         MacronutrientExtraction with basic nutritional data
#     """
#     chain = get_macronutrient_extraction_chain()
    
#     # Combine ingredients into a single analysis
#     combined_ingredients = ", ".join(ingredients)
    
#     try:
#         result = chain.invoke({
#             "ingredients": combined_ingredients,
#             "meal_type": meal_type,
#             "preparation_method": preparation_method,
#             "portion_size": portion_size,
#             "additional_notes": additional_notes
#         })
#         return result
#     except Exception as e:
#         print(f"Error in basic macronutrient analysis: {str(e)}")
#         raise
