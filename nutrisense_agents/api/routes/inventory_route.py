from fastapi import APIRouter, Query, HTTPException, Body
from nutrisense_agents.ai_companion.tools.react_tools import get_user_inventory_tool, check_expiring_ingredients_tool,suggest_recipes_from_stock_tool,generate_shopping_list_tool
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
def get_expiring_ingredients(user_uuid: str = Query(...)):
    """
    Devuelve los ingredientes del inventario que vencen HOY.
    """
    try:
        config = RunnableConfig(configurable={"user_uuid": user_uuid})
        return {
            "expiring_ingredients": check_expiring_ingredients_tool.invoke(input={}, config=config)
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