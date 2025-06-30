from langchain_core.prompts import ChatPromptTemplate
from nutrisense_agents.ai_companion.schemas.nutrition_plan_schema import NutritionPlanSchema, NutritionTargetSchema, SummarySchema
from nutrisense_agents.config.agent_config import get_chat_model
from nutrisense_agents.ai_companion.prompts.nutrition_plan_prompt import NUTRITION_PLAN_PROMPT, NUTRITION_TARGETS_PROMPT, SUMMARY_PROMPT

def nutrition_target_agent():
    model = get_chat_model(model_type="gpt", temperature=0.3).with_structured_output(NutritionTargetSchema)
    prompt = ChatPromptTemplate([
    ("system", NUTRITION_TARGETS_PROMPT),
    ("human", 
    """
    Edad: {age}
    Género: {gender}
    Peso actual (kg): {weight}
    Altura (cm): {height}
    Nivel de actividad física: {activity_level}
    Objetivo principal: {goal}
    
    Preferencias alimentarias: {preferences}
    Alergias o intolerancias: {allergies}
    Condiciones médicas: {medical_conditions}
    
    Registro de un día promedio:
    - Desayuno: {breakfast}
    - Almuerzo: {lunch}
    - Merienda: {snack}
    - Cena: {dinner}
    
    Contexto laboral y rutina diaria:
    - Modalidad laboral: {work_mode}
    - Turnos: {shift_type}
    - Lugar de almuerzo: {lunch_place}
    
    Organización alimentaria:
    - ¿Quién cocina?: {who_cooks}
    - ¿Quién hace las compras?: {who_shops}
    - ¿Cocinás solo para vos?: {cook_for_others}
    
    Fin de semana vs semana: {weekend_diff}
    
    Habilidades y tiempos para cocinar:
    - Frecuencia de cocina: {cooking_frequency}
    - Tiempo disponible: {cooking_time}
    - Gustos por cocinar: {cooking_likes}
    - Frecuencia de delivery o ultraprocesados: {ultraprocessed_frequency}
    
    Historia del peso:
    - Peso estable en otras etapas: {weight_history}
    - Cambios recientes: {weight_changes}
    - Eventos asociados: {weight_events}
    
    Hábitos:
    - Dificultades actuales: {current_difficulties}
    - ¿Comés por hambre o emoción?: {emotional_eating}
    - Snacks/picoteos entre comidas: {snacking}
    - Consumo de alcohol: {alcohol_intake}
    """
    )
])

    chain = prompt | model

    return chain

def get_summary_agent():
    """
    Agente para generar resumen conversacional del plan nutricional
    """
    model = get_chat_model(model_type="gpt", temperature=0.3).with_structured_output(SummarySchema)
    
    prompt = ChatPromptTemplate([
        ("system", SUMMARY_PROMPT),
        ("human", 
         """
         Información del usuario:
         Edad: {age}
         Género: {gender}
         Peso: {weight}kg
         Altura: {height}cm
         Objetivo: {goal}
         Actividad física: {activity_level}
         
         Preferencias: {preferences}
         Alergias: {allergies}
         Condiciones médicas: {medical_conditions}
         
         Situación actual:
         - Desayuno habitual: {breakfast}
         - Almuerzo habitual: {lunch}
         - Merienda habitual: {snack}
         - Cena habitual: {dinner}
         
         Contexto de vida:
         - Trabajo: {work_mode}
         - Turnos: {shift_type}
         - Quién cocina: {who_cooks}
         - Frecuencia de cocina: {cooking_frequency}
         - Tiempo para cocinar: {cooking_time}
         - Consumo ultraprocesados: {ultraprocessed_frequency}
         
         Dificultades actuales: {current_difficulties}
         Come por emoción: {emotional_eating}
         Picotea entre comidas: {snacking}
         
         OBJETIVOS NUTRICIONALES CALCULADOS:
         - Calorías diarias: {daily_calories_target}
         - Proteína: {daily_protein_target}g
         - Carbohidratos: {daily_carbs_target}g
         - Grasas: {daily_fat_target}g
         - Peso objetivo: {weight_target}kg
         
         PLAN NUTRICIONAL GENERADO:
         {nutrition_plan_description}
         
         Crea un resumen conversacional que explique este plan de manera personal y motivadora.
         """
        )
    ])
    
    chain = prompt | model
    return chain

def get_nutrition_plan_agent_chain():
    model = get_chat_model(model_type="gpt", temperature=0.3).with_structured_output(NutritionPlanSchema)

    prompt = ChatPromptTemplate([
    ("system", NUTRITION_PLAN_PROMPT),
    ("human", 
    """
    Edad: {age}
    Género: {gender}
    Peso actual (kg): {weight}
    Altura (cm): {height}
    Nivel de actividad física: {activity_level}
    Objetivo principal: {goal}
    
    Preferencias alimentarias: {preferences}
    Alergias o intolerancias: {allergies}
    Condiciones médicas: {medical_conditions}
    
    Registro de un día promedio:
    - Desayuno: {breakfast}
    - Almuerzo: {lunch}
    - Merienda: {snack}
    - Cena: {dinner}
    
    Contexto laboral y rutina diaria:
    - Modalidad laboral: {work_mode}
    - Turnos: {shift_type}
    - Lugar de almuerzo: {lunch_place}
    
    Organización alimentaria:
    - ¿Quién cocina?: {who_cooks}
    - ¿Quién hace las compras?: {who_shops}
    - ¿Cocinás solo para vos?: {cook_for_others}
    
    Fin de semana vs semana: {weekend_diff}
    
    Habilidades y tiempos para cocinar:
    - Frecuencia de cocina: {cooking_frequency}
    - Tiempo disponible: {cooking_time}
    - Gustos por cocinar: {cooking_likes}
    - Frecuencia de delivery o ultraprocesados: {ultraprocessed_frequency}
    
    Historia del peso:
    - Peso estable en otras etapas: {weight_history}
    - Cambios recientes: {weight_changes}
    - Eventos asociados: {weight_events}
    
    Hábitos:
    - Dificultades actuales: {current_difficulties}
    - ¿Comés por hambre o emoción?: {emotional_eating}
    - Snacks/picoteos entre comidas: {snacking}
    - Consumo de alcohol: {alcohol_intake}

    Objetivos nutricionales diarios:
    - Calorías objetivo: {daily_calories_target}
    - Proteína objetivo (g): {daily_protein_target}
    - Carbohidratos objetivo (g): {daily_carbs_target}
    - Grasas objetivo (g): {daily_fat_target}
    - Peso objetivo (kg): {weight_target}
    """
    )
])

    chain = prompt | model

    return chain