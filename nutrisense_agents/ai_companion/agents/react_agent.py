"""
Módulo para la construcción del React Agent de NutriSense.

Este módulo se limita a:
1. Recuperar el modelo de chat
2. Obtener las tools protegidas
3. Construir el grafo React Agent con LangGraph
"""

from typing import Dict, Any

from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from nutrisense_agents.config.agent_config import get_chat_model
from nutrisense_agents.ai_companion.MCPs.mcp_tools import get_mcp_tools
from nutrisense_agents.ai_companion.prompts.react_prompt import REACT_PROMPT

async def create_nutrisense_react_agent(user_uid: str, user_sheet: str, user_plan: str):
    """
    Compila y devuelve el React Agent ya preparado para el usuario.
    
    Args:
        user_uid: ID del usuario
        user_sheet: Ficha del usuario
        user_plan: Plan nutricional del usuario
    """
    model = get_chat_model("claude")
    tools = await get_mcp_tools(user_uid=user_uid)

    # Escapar llaves para evitar conflictos con ChatPromptTemplate
    user_sheet_escaped = str(user_sheet).replace('{', '{{').replace('}', '}}')
    user_plan_escaped = str(user_plan).replace('{', '{{').replace('}', '}}')

    # Construimos el prompt con el contexto del usuario y placeholder para mensajes
    template = ChatPromptTemplate.from_messages([
        ("system", f"{REACT_PROMPT}\n\nContexto del usuario:\nFicha: {user_sheet_escaped}\nPlan Nutricional: {user_plan_escaped}"),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    return create_react_agent(model, tools, prompt=template)

# react_agent = create_nutrisense_react_agent(
#     user_uid="616c059d-fc52-4b88-a62b-80e2e774f896", 
#     user_sheet="Hola, gracias por compartir toda esta información. Tu objetivo principal es ganar masa muscular y, para eso, hemos calculado que necesitas unas 2500 calorías al día, con 135 gramos de proteína, 340 gramos de carbohidratos y 70 gramos de grasas. Estos valores están pensados para acompañar tu actividad física moderada y ayudarte a construir músculo de manera efectiva. Como trabajas desde casa y tienes turnos rotativos, entiendo que tu rutina puede ser un poco variable y que el tiempo para cocinar es limitado. Por eso, las directrices que te propongo son flexibles y fáciles de adaptar: intenta no saltarte el desayuno, ya que incluir una comida más completa por la mañana te ayudará a alcanzar tus requerimientos calóricos y de proteína. Además, dado que sueles picotear entre comidas, es importante que esos snacks sean nutritivos, como yogur, frutos secos o fruta, para que contribuyan a tu objetivo de ganancia muscular. Recuerda que no necesitas complicarte con recetas elaboradas; lo importante es que cada comida principal incluya una buena fuente de proteína, carbohidratos y algo de grasa saludable. Aprovecha tu flexibilidad alimentaria para variar y disfrutar de lo que comes. Si logras mantenerte cerca de estos objetivos diarios y planificas un poco tus comidas, vas a notar resultados positivos en tu masa muscular y energía. ¡Ánimo, estás en el camino correcto!",
#     user_plan='{"imc": 22.04, "edad": 22, "peso": 60.0, "altura": 165, "nombre": "No especificado", "profile_name": "Perfil Nutricional - Ganancia Muscular Masculino 22 años", "user_summary": "Varón de 22 años, 60 kg y 165 cm de altura, con nivel de actividad física moderado y objetivo principal de ganancia muscular. No presenta alergias, intolerancias ni condiciones médicas, y tiene una actitud flexible hacia la alimentación, sin restricciones alimentarias. Su rutina diaria se caracteriza por desayunar solo té matcha, almorzar y cenar en casa lo que haya disponible, sin meriendas y con snacks frecuentes entre comidas. Trabaja desde casa con turnos rotativos, comparte la cocina y las compras, y cocina principalmente para sí mismo, aunque dispone de poco tiempo y muestra neutralidad hacia la cocina. No consume alcohol ni recurre a delivery o ultraprocesados. Su objetivo nutricional es alcanzar 2500 kcal diarias, con 135 g de proteína, 340 g de carbohidratos y 70 g de grasas.", "nivel_actividad": "Moderado", "habitos_y_contexto": "En cuanto a los hábitos alimentarios, el usuario suele desayunar únicamente té matcha alrededor de las 9 de la mañana, almorzar y cenar en casa lo que esté disponible, generalmente a las 12 y entre las 8 o 9 de la noche respectivamente, y no realiza meriendas. Los snacks o picoteos entre comidas son frecuentes. Su contexto laboral es en modalidad home office con turnos rotativos, lo que aporta flexibilidad pero también variabilidad en los horarios. El almuerzo se realiza en casa, y tanto la cocina como las compras son actividades compartidas, aunque cocina principalmente para sí mismo. La frecuencia de cocina es semanal, con muy poco tiempo disponible y una actitud neutral hacia la preparación de alimentos. No consume delivery ni productos ultraprocesados, y su organización alimentaria es flexible entre semana y fines de semana.", "objetivo_principal": "Ganancia muscular", "objetivos_nutricionales": {"carbs": 340, "grasas": 70, "protein": 135, "calories": 2500}, "dificultades_y_observaciones": "El usuario reporta como principal dificultad la falta de tiempo para la preparación de comidas, lo que influye en la organización de su alimentación diaria. A pesar de no presentar antecedentes de cambios de peso ni eventos asociados, la frecuencia de snacks entre comidas y la ausencia de meriendas formales son aspectos destacados de su patrón alimentario. No se identifican consumos de alcohol ni de alimentos ultraprocesados, y su alimentación se basa en la disponibilidad y practicidad, dada la limitación de tiempo y la flexibilidad de su rutina.", "preferencias_y_restricciones": "El usuario manifiesta una preferencia alimentaria amplia, indicando que le gusta todo, y no reporta alergias, intolerancias ni condiciones médicas relevantes. Esto permite una alimentación variada y sin restricciones específicas, facilitando la adaptación a diferentes tipos de alimentos y preparaciones."}'
# )