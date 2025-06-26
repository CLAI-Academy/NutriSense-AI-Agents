from fastapi import APIRouter
from nutrisense_agents.api.routes.nutrition_plan_route import router as nutrition_plan_router
from nutrisense_agents.api.routes.img_analysis_route import router as img_analysis_router
from nutrisense_agents.api.routes.text_analysis_route import router as text_analysis_router

router = APIRouter()

# Incluir las rutas en el router principal
router.include_router(nutrition_plan_router, prefix="/api")
router.include_router(img_analysis_router, prefix="/api")
router.include_router(text_analysis_router, prefix="/api")

