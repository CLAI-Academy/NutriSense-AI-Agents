from fastapi import APIRouter
from nutrisense_agents.api.routes.nutrition_plan_route import router as nutrition_plan_router
from nutrisense_agents.api.routes.food_analysis_route import router as food_analysis_router
from nutrisense_agents.api.routes.user_nutrition_profile_route import router as user_profile_router
# from nutrisense_agents.api.routes.macronutrient_route import router as macronutrient_router  # NO UTILIZADO

router = APIRouter()

# Incluir las rutas en el router principal
router.include_router(nutrition_plan_router, prefix="/api")
router.include_router(food_analysis_router, prefix="/api")
router.include_router(user_profile_router, prefix="/api")
# router.include_router(macronutrient_router, prefix="/api")  # NO UTILIZADO

