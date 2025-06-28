from fastapi import APIRouter
from nutrisense_agents.api.routes.macronutrient_route import router as macronutrient_router

router = APIRouter()
router.include_router(macronutrient_router, prefix="/api")