from fastapi import APIRouter, Query, HTTPException, Body
from nutrisense_agents.ai_companion.tools.react_tools import get_user_inventory_tool, check_expiring_ingredients_tool,suggest_recipes_from_stock_tool,generate_shopping_list_tool,suggest_recipes_for_expiring_tool
from langchain_core.runnables import RunnableConfig
from nutrisense_agents.ai_companion.schemas.tools_schemas.react_input_schemas import ShoppingListInput

router = APIRouter()

@router.get("/inventory")
def get_user_inventory_route(user_uuid: str = Query(...)):
    """
    Endpoint para testear get_user_inventory_tool usando RunnableConfig.
    """
    try:
        config = RunnableConfig(configurable={"user_uuid": user_uuid})
        return {"inventory": get_user_inventory_tool.invoke(input={}, config=config)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/expiring")
def get_expiring_ingredients(
    user_uuid: str = Query(..., description="ID único del usuario"),
    days_ahead: int = Query(0, description="Días hacia adelante para buscar próximos vencimientos"),
    days_behind: int = Query(0, description="Días hacia atrás para buscar vencidos recientes")
):
    """
    Devuelve los ingredientes del inventario según la fecha de vencimiento.

    - expired: vencidos en los últimos `days_behind` días.
    - expiring_today: vencen exactamente hoy.
    - expiring_soon: vencen en los próximos `days_ahead` días.

    Ejemplos:
    - Solo lo que vence hoy → days_ahead=0, days_behind=0
    - Vencidos últimos 7 días → days_ahead=0, days_behind=7
    - Próximos 3 días → days_ahead=3, days_behind=0
    """
    try:
        config = RunnableConfig(configurable={"user_uuid": user_uuid})
        return {
            "expiring_ingredients": check_expiring_ingredients_tool.invoke(
                input={"days_ahead": days_ahead, "days_behind": days_behind},
                config=config
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@router.get("/inventory/suggested_recipes")
def get_suggested_recipes(user_uuid: str = Query(...)):
    """
    Sugiere recetas que el usuario puede preparar según su inventario actual.
    """
    try:
        config = RunnableConfig(configurable={"user_uuid": user_uuid})
        return {
            "suggested_recipes": suggest_recipes_from_stock_tool.invoke(input={}, config=config)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/inventory/shopping_list")
def get_shopping_list(
    user_uuid: str = Query(...),
    body: ShoppingListInput = Body(...)  
):
    """
    Genera una lista de compras en base a recetas seleccionadas y el inventario del usuario.
    """
    try:
        config = RunnableConfig(configurable={"user_uuid": user_uuid})
        return {
            "shopping_list": generate_shopping_list_tool.invoke(
                input=body.model_dump(),
                config=config
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/recipes/expiring")
def get_recipes_for_expiring(
    user_uuid: str = Query(..., description="ID único del usuario"),
    days_ahead: int = Query(3, description="Días hacia adelante para considerar ingredientes por vencer")
):
    """
    Devuelve recetas sugeridas en base a los ingredientes que vencen en los próximos `days_ahead` días.
    Prioriza:
    1. Ingredientes con fecha de vencimiento más próxima.
    2. Recetas con mayor porcentaje de coincidencia de ingredientes por vencer.
    """
    try:
        config = RunnableConfig(configurable={"user_uuid": user_uuid})
        return {
            "recipes": suggest_recipes_for_expiring_tool.invoke(
                input={"days_ahead": days_ahead},
                config=config
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
