from fastapi import APIRouter
from nutrisense_agents.api.services.nutrition_plan_service import generate_nutrition_plan_service
from nutrisense_agents.ai_companion.schemas.nutrition_plan_schema import (
    NutritionPlanInputSchema,
    
)

# Define el router para las rutas
router = APIRouter()

# Ruta para generar un plan nutricional
@router.post("/nutrition-plan")
async def generate_nutrition_plan(input_data: NutritionPlanInputSchema):
    """
    Genera un plan nutricional y lo guarda en Supabase.
    """
    result = generate_nutrition_plan_service(
        user_data=input_data.model_dump(),
        user_id=input_data.user_id
    )
    return result
