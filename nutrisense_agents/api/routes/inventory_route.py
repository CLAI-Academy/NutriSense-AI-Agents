from fastapi import APIRouter,Query,HTTPException
from nutrisense_agents.ai_companion.react_agent.tools.react_tools import get_user_inventory

router = APIRouter()

@router.get("/inventory")
def get_user_inventory_route(user_id: str = Query(..., description="UUID del usuario")):
    """ 
    Endpoint REST que reutiliza la tool get_user_inventory para devolver el inventario del usuario
    """
    try:
        inventory = get_user_inventory(user_id)
        return {"inventory": inventory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    