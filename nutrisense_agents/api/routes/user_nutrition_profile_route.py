from fastapi import APIRouter
from nutrisense_agents.api.services.user_profile_service import generate_user_profile_service
from nutrisense_agents.ai_companion.schemas.user_profile_schema import (
    UserProfileInputSchema,
    
)

# Define el router para las rutas
router = APIRouter()

# Ruta para generar un plan nutricional
@router.post("/user-nutrition-profile")
async def generate_user_nutrition_profile(input_data: UserProfileInputSchema):
    """
    Genera un perfil nutricional y lo guarda en Supabase.
    """
    result = generate_user_profile_service(
        user_data=input_data.model_dump(),
        user_id=input_data.user_id
    )
    return result
