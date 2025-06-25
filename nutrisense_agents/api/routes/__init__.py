from fastapi import APIRouter
from nutrisense_agents.api.routes.nutrition_plan_route import router as nutrition_plan_router

router = APIRouter()

# Incluir la ruta  de nutrición en el router principal
router.include_router(nutrition_plan_router, prefix="/api")

