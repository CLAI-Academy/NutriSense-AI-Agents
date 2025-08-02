"""
react_tools.py

Herramientas disponibles para el React Agent.
Estas tools se registran con @tool y permiten consultar información nutricional
y del inventario del usuario desde Supabase.
"""
from langchain_core.tools import tool
from nutrisense_agents.db.supabase.client import SupabaseClient


@tool
def get_user_inventory(user_id: str) -> str:
    """
    Devuelve el inventario del usuario de Supabase,
    incluyendo nombre del ingrediente, cantidad, unidad y fecha de vencimiento
    """

    supabase = SupabaseClient().supabase

    # Obtener el inventario filtrado por usuario
    inventory = supabase\
        .from_('user_inventory') \
        .select("ingredient_id,quantity,unit,expiry_date") \
        .eq('user_id', user_id.strip()) \
        .execute()
    
    print(f"🔍 DEBUG: inventory: {inventory}")
    print(f"🔍 DEBUG: inventory.data: {inventory.data}")
    
    if not inventory.data:
        return []
    
    # Obtener lista unica de ingredientes_ids
    ingredient_ids = list(set(item['ingredient_id'] for item in inventory.data))

    # Buscar nombre de ingredientes
    ingredients_lookup = supabase.client \
        .from_('ingredients') \
        .select("id,name") \
        .in_("id", ingredient_ids) \
        .execute()
        
    
    name_map = {item['id']: item['name'] for item in ingredients_lookup.data}

    # Formatear resultado
    result = []
    for item in inventory.data:
        result.append({
            "ingredient" : name_map.get(item["ingredient_id"], f"ID {item['ingredient_id']}"),
            "quantity" : item["quantity"],
            "unit" : item["unit"],
            "expiry_date" : item["expiry_date"]
        })

    return result