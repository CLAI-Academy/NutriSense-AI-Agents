import sys, logging
from typing import Optional
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid

from nutrisense_agents.ai_companion.schemas.tools_schemas.react_input_schemas import RecipeList, MealPlanInput, PlannedMealInput
from nutrisense_agents.db.supabase.client import get_supabase_client
from nutrisense_agents.ai_companion.agents.enrich_recipes_agent import enrich_ingredients_nutrition



logging.basicConfig(level=logging.ERROR, handlers=[logging.StreamHandler(sys.stderr)])
log = logging.getLogger(__name__)

# Modelos para validar la entrada de recetas

# Constante de tablas permitidas
ALLOWED_TABLES = {
    "ingredients",
    "recipes",
    "recipe_ingredients",
    "meal_plans",
    "planned_meals",
    "food_diary",
    "food_photo_analysis",
    "daily_nutrition_summary",
    "user_inventory",
    "shopping_lists",
    "shopping_list_items",
    "user_streak",
}


class SupabaseTools:
    def __init__(self):
        self.sb = get_supabase_client()
        self.ALLOWED_TABLES = ALLOWED_TABLES

    def add_planned_meal(self, data: RecipeList, user_uuid: str) -> Optional[List[int]]:
        """
        Añade una lista de comidas planificadas para el usuario.
        Tras crear la lista de comidas, se debe mostrar al usuario, qué días debe cocinar, que recetas debe preparar y como guardarlas
        para que sea lo más óptimo posible. 
        """
        
        created_recipe_ids = []
        
        try:
            # Procesar cada receta en la lista
            for recipe_data in data.recipes:
                # 0. Verificar si ya existe una receta con el mismo nombre
                existing_recipe = self.sb.table("recipes").select("id").eq("title", recipe_data.name).execute()
                
                if existing_recipe.data and len(existing_recipe.data) > 0:
                    recipe_id = existing_recipe.data[0]["id"]
                    created_recipe_ids.append(recipe_id)
                    log.info(f"Receta '{recipe_data.name}' ya existe con ID: {recipe_id}")
                    continue
                
                # 1. Verificar qué ingredientes ya existen en la base de datos
                existing_ingredients = {}
                missing_ingredients = []
                
                for ing in recipe_data.ingredients:
                    ingredient_name = ing.name.lower().strip()
                    
                    # Buscar el ingrediente en la base de datos
                    existing = self.sb.table("ingredients").select("*").eq("name", ingredient_name).execute()
                    
                    if existing.data:
                        # El ingrediente ya existe
                        existing_ingredients[ingredient_name] = existing.data[0]
                    else:
                        # El ingrediente no existe, necesita ser enriquecido
                        missing_ingredients.append({
                            "id": None,
                            "name": ingredient_name,
                            "default_unit": ing.unit
                        })
                
                # 2. Enriquecer ingredientes faltantes con información nutricional
                if missing_ingredients:
                    nutrition_data = enrich_ingredients_nutrition({"ingredients": missing_ingredients})
                    
                    # Insertar ingredientes enriquecidos
                    for update in nutrition_data.get("updates", []):
                        ingredient_data = {
                            "name": update["name"].lower().strip(),
                            "category": update["category"],
                            "calories_per_100g": update["calories_per_100g"],
                            "protein_per_100g": update["protein_per_100g"],
                            "carbs_per_100g": update["carbs_per_100g"],
                            "fat_per_100g": update["fat_per_100g"],
                            "fiber_per_100g": update["fiber_per_100g"],
                            "default_unit": next((ing["default_unit"] for ing in missing_ingredients 
                                                if ing["name"] == update["name"]), "g"),
                            "nutrition_status": "verified"
                        }
                        
                        # Insertar el ingrediente enriquecido
                        result = self.sb.table("ingredients").insert(ingredient_data).execute()
                        if result.data:
                            existing_ingredients[update["name"]] = result.data[0]
                    
                    # Insertar ingredientes que dieron error como básicos
                    for error in nutrition_data.get("errors", []):
                        if error["name"] not in ["input_validation", "llm_error"]:
                            basic_ingredient = {
                                "name": error["name"].lower().strip(),
                                "default_unit": next((ing["default_unit"] for ing in missing_ingredients 
                                                    if ing["name"] == error["name"]), "g"),
                                "nutrition_status": "pending"
                            }
                            
                            result = self.sb.table("ingredients").insert(basic_ingredient).execute()
                            if result.data:
                                existing_ingredients[error["name"]] = result.data[0]
                
                # 3. Insertar la receta
                # Calcular totales nutricionales de la receta
                total_calories = 0
                total_protein = 0
                total_carbs = 0
                total_fat = 0
                
                for ing in recipe_data.ingredients:
                    ingredient_name = ing.name.lower().strip()
                    
                    if ingredient_name in existing_ingredients:
                        # Obtener datos nutricionales del ingrediente
                        ingredient = existing_ingredients[ingredient_name]
                        quantity = float(ing.quantity)
                        
                        # Convertir a gramos si es necesario para el cálculo
                        weight_in_grams = quantity
                        if ing.unit.lower() not in ["g", "gr", "gramo", "gramos"]:
                            # Para simplificar, asumimos una conversión básica
                            # En un caso real, habría que implementar conversiones más precisas
                            if ing.unit.lower() in ["kg", "kilo", "kilos"]:
                                weight_in_grams = quantity * 1000
                        
                        # Calcular aporte nutricional (regla de 3)
                        calories = (ingredient.get("calories_per_100g", 0) or 0) * weight_in_grams / 100
                        protein = (ingredient.get("protein_per_100g", 0) or 0) * weight_in_grams / 100
                        carbs = (ingredient.get("carbs_per_100g", 0) or 0) * weight_in_grams / 100
                        fat = (ingredient.get("fat_per_100g", 0) or 0) * weight_in_grams / 100
                        
                        # Sumar al total
                        total_calories += calories
                        total_protein += protein
                        total_carbs += carbs
                        total_fat += fat
                
                recipe_insert_data = {
                    "title": recipe_data.name,
                    "description": recipe_data.description,
                    "instructions": recipe_data.instructions,
                    "meal_type": recipe_data.meal_type.lower(),
                    "difficulty_level": "easy",  # default
                    "is_public": False,  # privada por defecto
                    "total_calories": round(total_calories, 2),
                    "total_protein": round(total_protein, 2),
                    "total_carbs": round(total_carbs, 2),
                    "total_fat": round(total_fat, 2)
                }
                
                recipe_result = self.sb.table("recipes").insert(recipe_insert_data).execute()
                
                if not recipe_result.data:
                    log.error(f"Error insertando receta: {recipe_data.name}")
                    continue
                    
                recipe_id = recipe_result.data[0]["id"]
                created_recipe_ids.append(recipe_id)
                
                # 4. Insertar relaciones recipe_ingredients
                for ing in recipe_data.ingredients:
                    ingredient_name = ing.name.lower().strip()
                    
                    if ingredient_name in existing_ingredients:
                        ingredient_id = existing_ingredients[ingredient_name]["id"]
                        
                        recipe_ingredient_data = {
                            "recipe_id": recipe_id,
                            "ingredient_id": ingredient_id,
                            "quantity": float(ing.quantity),
                            "unit": ing.unit
                        }
                        
                        self.sb.table("recipe_ingredients").insert(recipe_ingredient_data).execute()
                
            return created_recipe_ids if created_recipe_ids else None
                
        except Exception as e:
            log.error(f"Error creating recipes: {str(e)}")
            return None

    def create_meal_plan(self, data: MealPlanInput, user_uuid: str) -> Optional[str]:
        """
        Crea un plan de comidas semanal base para el usuario.
        
        Args:
            data: Datos del plan de comidas (fecha inicio, objetivos, preferencias)
            user_uuid: UUID del usuario
            
        Returns:
            ID del plan de comidas creado o None si hay error
        """
        try:
            # Verificar si ya existe un plan para esa semana y usuario
            week_start_date = data.week_start_date.isoformat()
            existing_plan = self.sb.table("meal_plans").select("id").eq("user_id", user_uuid).eq("week_start_date", week_start_date).execute()
            
            # Si ya existe un plan, devolver su ID
            if existing_plan.data and len(existing_plan.data) > 0:
                log.info(f"Plan de comidas ya existe para la semana {week_start_date}")
                return existing_plan.data[0]["id"]
            
            # Generar UUID para el plan de comidas
            meal_plan_id = str(uuid.uuid4())
            
            # Preparar datos para inserción
            meal_plan_data = {
                "id": meal_plan_id,
                "user_id": user_uuid,
                "week_start_date": week_start_date,
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insertar el plan de comidas
            result = self.sb.table("meal_plans").insert(meal_plan_data).execute()
            
            if result.data:
                log.info(f"Plan de comidas creado con ID: {meal_plan_id}")
                return meal_plan_id
            else:
                log.error("Error al crear el plan de comidas")
                return None
                
        except Exception as e:
            log.error(f"Error creating meal plan: {str(e)}")
            return None

    def add_planned_meal_to_schedule(self, data: PlannedMealInput, user_uuid: str) -> Optional[dict]:
        """
        Crea recetas y las programa automáticamente en un plan de comidas.
        Combina la lógica de add_planned_meal con la programación en planned_meals.
        
        Args:
            data: Datos con meal_plan_id, recetas y configuración de programación
            user_uuid: UUID del usuario
            
        Returns:
            Diccionario con IDs de recetas creadas y programación realizada
        """
        try:
            # 1. Crear las recetas usando la lógica existente
            recipe_list = RecipeList(recipes=data.recipes)
            created_recipe_ids = self.add_planned_meal(recipe_list, user_uuid)
            
            if not created_recipe_ids:
                log.error("No se pudieron crear las recetas")
                return None
            
            # 2. Si auto_schedule está activado, programar las recetas
            scheduled_meals = []
            if data.auto_schedule:
                # Obtener información de las recetas creadas
                recipe_info = []
                for recipe_id in created_recipe_ids:
                    recipe_data = self.sb.table("recipes").select("*").eq("id", recipe_id).execute()
                    if recipe_data.data:
                        recipe_info.append(recipe_data.data[0])
                
                # Programar las recetas en la semana
                day_counter = 0
                for recipe in recipe_info:
                    meal_type = recipe.get("meal_type", "lunch")
                    
                    # Determinar horario por tipo de comida
                    start_time = self._get_meal_start_time(meal_type)
                    
                    # Crear entrada en planned_meals
                    planned_meal_data = {
                        "id": str(uuid.uuid4()),
                        "meal_plan_id": data.meal_plan_id,
                        "recipe_id": recipe["id"],
                        "day_of_week": day_counter % 7,  # Distribuir en 7 días
                        "meal_type": meal_type,
                        "start_time": start_time,
                        "servings_planned": 1,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    result = self.sb.table("planned_meals").insert(planned_meal_data).execute()
                    if result.data:
                        scheduled_meals.append(result.data[0])
                    
                    day_counter += 1
            
            return {
                "created_recipe_ids": created_recipe_ids,
                "scheduled_meals": scheduled_meals,
                "meal_plan_id": data.meal_plan_id
            }
            
        except Exception as e:
            log.error(f"Error creating planned meals: {str(e)}")
            return None
    
    def _get_meal_start_time(self, meal_type: str) -> int:
        """Obtiene la hora de inicio por defecto para cada tipo de comida (en minutos desde medianoche)"""
        meal_times = {
            "breakfast": 8 * 60,    # 8:00 AM
            "lunch": 13 * 60,       # 1:00 PM  
            "dinner": 19 * 60,      # 7:00 PM
            "snack": 16 * 60        # 4:00 PM
        }
        return meal_times.get(meal_type.lower(), 12 * 60)  # Default 12:00 PM

    def optimize_meal_plan(self, meal_plan_id: str, user_uuid: str) -> Optional[dict]:
        """
        Analiza y optimiza un plan de comidas existente.
        
        Args:
            meal_plan_id: ID del plan de comidas a optimizar
            user_uuid: UUID del usuario
            
        Returns:
            Diccionario con análisis nutricional y recomendaciones
        """
        try:
            # 1. Obtener todas las comidas planificadas
            planned_meals = self.sb.table("planned_meals").select("*").eq("meal_plan_id", meal_plan_id).execute()
            
            if not planned_meals.data:
                log.warning(f"No se encontraron comidas planificadas para el plan {meal_plan_id}")
                return None
            
            # 2. Calcular totales nutricionales por día
            daily_nutrition = {}
            ingredients_needed = {}
            
            for meal in planned_meals.data:
                day = meal["day_of_week"]
                recipe_id = meal["recipe_id"]
                servings = meal["servings_planned"]
                
                # Obtener datos de la receta por separado
                recipe_data = self.sb.table("recipes").select("*").eq("id", recipe_id).execute()
                if not recipe_data.data:
                    log.warning(f"Receta {recipe_id} no encontrada")
                    continue
                recipe = recipe_data.data[0]
                
                # Inicializar día si no existe
                if day not in daily_nutrition:
                    daily_nutrition[day] = {
                        "total_calories": 0,
                        "total_protein": 0,
                        "total_carbs": 0,
                        "total_fat": 0,
                        "meals": []
                    }
                
                # Sumar nutrición del día
                daily_nutrition[day]["total_calories"] += (recipe.get("total_calories", 0) or 0) * servings
                daily_nutrition[day]["total_protein"] += (recipe.get("total_protein", 0) or 0) * servings
                daily_nutrition[day]["total_carbs"] += (recipe.get("total_carbs", 0) or 0) * servings
                daily_nutrition[day]["total_fat"] += (recipe.get("total_fat", 0) or 0) * servings
                
                daily_nutrition[day]["meals"].append({
                    "recipe_title": recipe["title"],
                    "meal_type": recipe["meal_type"],
                    "servings": servings
                })
                
                # 3. Obtener ingredientes necesarios
                try:
                    recipe_ingredients = self.sb.table("recipe_ingredients").select("""
                        *,
                        ingredients!inner(name, default_unit)
                    """).eq("recipe_id", recipe["id"]).execute()
                except Exception as e:
                    log.error(f"Error al obtener ingredientes para la receta {recipe.get('title', 'desconocida')}: {str(e)}")
                    recipe_ingredients = {"data": []}
                
                for ri in recipe_ingredients.data or []:
                    ingredient_name = ri["ingredients"]["name"]
                    quantity = ri["quantity"] * servings
                    unit = ri["unit"]
                    
                    if ingredient_name not in ingredients_needed:
                        ingredients_needed[ingredient_name] = {}
                    
                    if unit not in ingredients_needed[ingredient_name]:
                        ingredients_needed[ingredient_name][unit] = 0
                    
                    ingredients_needed[ingredient_name][unit] += quantity
            
            # 4. Crear recomendaciones
            recommendations = []
            weekly_totals = {
                "calories": sum(day["total_calories"] for day in daily_nutrition.values()),
                "protein": sum(day["total_protein"] for day in daily_nutrition.values()),
                "carbs": sum(day["total_carbs"] for day in daily_nutrition.values()),
                "fat": sum(day["total_fat"] for day in daily_nutrition.values())
            }
            
            # Analizar balance nutricional
            avg_daily_calories = weekly_totals["calories"] / 7
            if avg_daily_calories < 1500:
                recommendations.append("⚠️ Calorías muy bajas - considera añadir snacks saludables")
            elif avg_daily_calories > 2500:
                recommendations.append("⚠️ Calorías muy altas - considera reducir porciones")
            
            # Analizar distribución de macronutrientes
            total_macros = weekly_totals["protein"] + weekly_totals["carbs"] + weekly_totals["fat"]
            if total_macros > 0:
                protein_pct = (weekly_totals["protein"] * 4) / (weekly_totals["calories"]) * 100
                carbs_pct = (weekly_totals["carbs"] * 4) / (weekly_totals["calories"]) * 100
                fat_pct = (weekly_totals["fat"] * 9) / (weekly_totals["calories"]) * 100
                
                if protein_pct < 15:
                    recommendations.append("🥩 Considera añadir más proteínas")
                if carbs_pct > 60:
                    recommendations.append("🍞 Considera reducir carbohidratos")
                if fat_pct > 35:
                    recommendations.append("🥑 Considera reducir grasas")
            
            # 5. Sugerir días de meal prep
            meal_prep_days = self._suggest_meal_prep_days(daily_nutrition)
            
            return {
                "meal_plan_id": meal_plan_id,
                "daily_nutrition": daily_nutrition,
                "weekly_totals": weekly_totals,
                "avg_daily_calories": avg_daily_calories,
                "recommendations": recommendations,
                "ingredients_needed": ingredients_needed,
                "meal_prep_suggestions": meal_prep_days
            }
            
        except Exception as e:
            log.error(f"Error optimizing meal plan: {str(e)}")
            return None
    
    def _suggest_meal_prep_days(self, daily_nutrition: dict) -> list:
        """Sugiere los mejores días para hacer meal prep basado en la carga de cocina"""
        suggestions = []
        
        # Contar recetas por día
        for day, nutrition in daily_nutrition.items():
            meal_count = len(nutrition["meals"])
            day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            
            if meal_count >= 3:
                suggestions.append(f"📅 {day_names[day]}: {meal_count} comidas - ideal para meal prep")
        
        if not suggestions:
            suggestions.append("📅 Domingo: Día recomendado para meal prep semanal")
        
        return suggestions

    def get_meal_plan_summary(self, meal_plan_id: str, user_uuid: str) -> Optional[dict]:
        """
        Obtiene un resumen completo del plan de comidas con información práctica.
        
        Args:
            meal_plan_id: ID del plan de comidas
            user_uuid: UUID del usuario
            
        Returns:
            Diccionario con resumen del plan, días de cocina y recetas a preparar
        """
        try:
            # 1. Obtener información del plan
            meal_plan = self.sb.table("meal_plans").select("*").eq("id", meal_plan_id).eq("user_id", user_uuid).execute()
            
            if not meal_plan.data:
                log.warning(f"Plan de comidas {meal_plan_id} no encontrado")
                return None
            
            plan_info = meal_plan.data[0]
            
            # 2. Obtener comidas planificadas 
            try:
                planned_meals = self.sb.table("planned_meals").select("*").eq("meal_plan_id", meal_plan_id).execute()
            except Exception as e:
                log.error(f"Error getting meal plan summary: {str(e)}")
                return {
                    "meal_plan_id": meal_plan_id,
                    "message": "Error al obtener detalles del plan de comidas"
                }
            
            if not planned_meals.data:
                return {
                    "meal_plan_id": meal_plan_id,
                    "week_start_date": plan_info["week_start_date"],
                    "message": "No hay comidas planificadas en este plan"
                }
            
            # 3. Organizar por días
            day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            weekly_schedule = {}
            
            for meal in planned_meals.data:
                day = meal["day_of_week"]
                day_name = day_names[day]
                
                if day_name not in weekly_schedule:
                    weekly_schedule[day_name] = []
                
                try:
                    recipe_id = meal["recipe_id"]
                    # Obtener datos de la receta por separado
                    recipe_data = self.sb.table("recipes").select("*").eq("id", recipe_id).execute()
                    if not recipe_data.data:
                        log.warning(f"Receta {recipe_id} no encontrada")
                        continue
                    recipe = recipe_data.data[0]
                    
                    start_time_hours = meal["start_time"] // 60
                    start_time_minutes = meal["start_time"] % 60
                except Exception as e:
                    log.error(f"Error al acceder a la receta: {str(e)}")
                    log.error(f"Estructura de meal: {list(meal.keys())}")
                    continue
                
                weekly_schedule[day_name].append({
                    "time": f"{start_time_hours:02d}:{start_time_minutes:02d}",
                    "meal_type": meal["meal_type"],
                    "recipe_title": recipe["title"],
                    "servings": meal["servings_planned"],
                    "prep_time": recipe.get("prep_time", 0),
                    "cook_time": recipe.get("cook_time", 0),
                    "total_time": (recipe.get("prep_time", 0) or 0) + (recipe.get("cook_time", 0) or 0),
                    "calories": recipe.get("total_calories", 0)
                })
            
            # 4. Calcular días de cocina optimizados
            cooking_days = {}
            unique_recipes = {}
            
            for meal in planned_meals.data:
                try:
                    recipe_id = meal["recipe_id"]
                    # Obtener datos de la receta por separado
                    recipe_data = self.sb.table("recipes").select("*").eq("id", recipe_id).execute()
                    if not recipe_data.data:
                        log.warning(f"Receta {recipe_id} no encontrada")
                        continue
                    recipe = recipe_data.data[0]
                except Exception as e:
                    log.error(f"Error al acceder a la receta en meal_prep: {str(e)}")
                    log.error(f"Estructura de meal: {list(meal.keys())}")
                    continue
                
                if recipe_id not in unique_recipes:
                    unique_recipes[recipe_id] = {
                        "title": recipe["title"],
                        "total_time": (recipe.get("prep_time", 0) or 0) + (recipe.get("cook_time", 0) or 0),
                        "servings_needed": 0,
                        "days_used": []
                    }
                
                unique_recipes[recipe_id]["servings_needed"] += meal["servings_planned"]
                unique_recipes[recipe_id]["days_used"].append(day_names[meal["day_of_week"]])
            
            # 5. Sugerir días de cocina
            total_cooking_time = sum(recipe["total_time"] for recipe in unique_recipes.values())
            
            if total_cooking_time > 180:  # Más de 3 horas
                cooking_days["Domingo"] = "Meal prep principal - preparar base de ingredientes"
                cooking_days["Miércoles"] = "Meal prep medio - preparar comidas de jueves a sábado"
            else:
                cooking_days["Domingo"] = "Meal prep semanal - preparar todas las comidas"
            
            # 6. Crear lista de recetas por preparar
            recipes_to_prepare = []
            for recipe_id, recipe_info in unique_recipes.items():
                recipes_to_prepare.append({
                    "recipe": recipe_info["title"],
                    "total_servings": recipe_info["servings_needed"],
                    "time_needed": recipe_info["total_time"],
                    "days_used": recipe_info["days_used"]
                })
            
            return {
                "meal_plan_id": meal_plan_id,
                "week_start_date": plan_info["week_start_date"],
                "is_active": plan_info["is_active"],
                "weekly_schedule": weekly_schedule,
                "cooking_days": cooking_days,
                "recipes_to_prepare": recipes_to_prepare,
                "total_cooking_time": total_cooking_time,
                "summary": {
                    "total_meals": len(planned_meals.data),
                    "unique_recipes": len(unique_recipes),
                    "avg_calories_per_meal": sum(recipe_info.get("calories", 0) for recipe_info in weekly_schedule.values() for recipe_info in recipe_info if recipe_info.get("calories")) / len(planned_meals.data) if planned_meals.data else 0
                }
            }
            
        except Exception as e:
            log.error(f"Error getting meal plan summary: {str(e)}")
            return {
                "meal_plan_id": meal_plan_id,
                "message": "Error al obtener detalles del plan de comidas"
            }
        

    def get_user_data(
        self,
        table_name: str,
        user_uuid: str,
        extra_filters: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> list:
        """
        Obtiene todos los registros de una tabla específica que pertenecen al usuario.
        
        Permite aplicar filtros adicionales y limitar el número de resultados.
        
        INFORMACIÓN DISPONIBLE POR TABLA:
        
        PLANIFICACIÓN:
        • meal_plans: Planes de comida semanales (week_start_date, is_active)
        • planned_meals: Comidas planificadas específicas (day_of_week, meal_type, recipe_id, 
          start_time, servings_planned)
        
        REGISTRO Y SEGUIMIENTO:
        • food_diary: Diario nutricional diario con alimentos consumidos, cantidades, información 
          nutricional, hora de consumo, ubicación, contexto, estado de ánimo ocasional
        • daily_nutrition_summary: Resúmenes nutricionales diarios agregados con totales vs objetivos 
          y puntuación de adherencia
        
        INVENTARIO Y COMPRAS:
        • user_inventory: Inventario personal de ingredientes (quantity, unit, expiry_date, location)
        • shopping_lists: Listas de compra (name, status, meal_plan_id, total_estimated_cost)
        • shopping_list_items: Items específicos de listas de compra con cantidades necesarias, 
          disponibles y a comprar
        
        GAMIFICACIÓN:
        • user_streak: Rachas de cumplimiento de objetivos (current_streak, best_streak, 
          last_target_date)
        
        Args:
            table_name: Nombre de la tabla a consultar (debe estar en ALLOWED_TABLES)
            user_uuid: UUID del usuario para filtrar los datos
            extra_filters: Filtros adicionales a aplicar (opcional)
            limit: Límite de resultados a retornar (opcional)
            
        Returns:
            Lista de registros que coinciden con los criterios de búsqueda
        """
        if table_name not in self.ALLOWED_TABLES:
            raise ValueError(f"Tabla «{table_name}» no permitida")

        query = self.sb.table(table_name).select("*").eq("user_id", user_uuid)

        if extra_filters:
            for col, val in extra_filters.items():
                query = query.eq(col, val)

        if limit:
            query = query.limit(limit)

        resp = query.execute()
        return resp.data or []
    
    def get_user_inventory(self, user_uuid: str) -> list:
        """ Devuelve el inventario actual del usuario, incluyendo:
        Nombre del ingrediente (buscado manualmente)
        - Cantidad
        - Unidad
        - Fecha de vencimiento
        """
        try:
            # 1. Obtener el inventario del usuario
            inventory_response = (
                self.sb.table("user_inventory")
                .select("ingredient_id, quantity, unit, expiry_date")
                .eq("user_id", user_uuid.strip())
                .execute()
            )

            inventory_data = inventory_response.data or []
            if not inventory_data:
                return []

            # 2. Extraer IDs únicos de ingredientes
            ingredient_ids = list({
                item["ingredient_id"]
                for item in inventory_data
                if item.get("ingredient_id")
            })

            if not ingredient_ids:
                return []

            # 3. Buscar nombres de ingredientes
            ingredients_response = (
                self.sb.table("ingredients")
                .select("id, name")
                .in_("id", ingredient_ids)
                .execute()
            )

            ingredients_data = ingredients_response.data or []
            name_map = {item["id"]: item["name"] for item in ingredients_data}

            # 4. Formatear el resultado final
            result = []
            for item in inventory_data:
                ingredient_name = name_map.get(item["ingredient_id"], f"ID {item['ingredient_id']}")
                result.append({
                    "ingredient_name": ingredient_name,
                    "quantity": item["quantity"],
                    "unit": item["unit"],
                    "expiry_date": item["expiry_date"]
                })

            return result

        except Exception as e:
            log.error(f"Error en get_user_inventory: {e}")
            return []

    def get_ingredients_expiry_range(self, user_uuid: str, days_ahead: int = 3, days_behind: int = 0) -> dict:
        """
        Devuelve ingredientes del inventario agrupados en:
        - expired: vencidos en los últimos `days_behind` días
        - expiring_today: vencen exactamente hoy
        - expiring_soon: vencen en los próximos `days_ahead` días
        """
        try:
            inventory = self.get_user_inventory(user_uuid)

            today = datetime.today().date()

            result = {"expired": [], "expiring_today": [], "expiring_soon": []}
            
            for item in inventory:
                expiry_raw = item.get("expiry_date")
                if not expiry_raw:
                    continue

                try:
                    expiry_date = datetime.strptime(expiry_raw[:10], "%Y-%m-%d").date()
                except ValueError:
                    continue

                delta_days = (expiry_date - today).days

                if delta_days < 0 and abs(delta_days) <= days_behind:
                    result["expired"].append(item)
                elif delta_days == 0:
                    result["expiring_today"].append(item)
                elif 0 < delta_days <= days_ahead:
                    result["expiring_soon"].append(item)

            return result

        except Exception as e:
            log.error(f"Error en get_ingredients_by_expiry_range: {e}")
            return {"expired": [], "expiring_today": [], "expiring_soon": []}

    def get_suggested_recipes_by_inventory(self, user_uuid: str) -> list:
        """
        Devuelve una lista de recetas recomendadas según los ingredientes del inventario del usuario.
        Para cada receta, calcula cuántos ingredientes tiene disponibles y cuáles le faltan.
        """
        try:
            # 1. Obtener inventario del usuario
            inventory = (
                self.sb.table("user_inventory")
                .select("ingredient_id, quantity, unit")
                .eq("user_id", user_uuid)
                .execute()
            ).data or []

            if not inventory:
                return []

            inventory_map = {
                item["ingredient_id"]: {
                    "quantity": float(item["quantity"]),
                    "unit": item["unit"]
                }
                for item in inventory
                if item.get("ingredient_id")
            }

            # 2. Obtener todas las recetas y sus ingredientes
            recipe_ingredients = (
                self.sb.table("recipe_ingredients")
                .select("recipe_id, ingredient_id, quantity, unit, recipes(title), ingredients(name)")
                .execute()
            ).data or []

            # 3. Agrupar ingredientes por receta
            recipes_map = {}
            for ri in recipe_ingredients:
                recipe_id = ri["recipe_id"]
                recipe_title = ri["recipes"]["title"]
                ingredient_id = ri["ingredient_id"]
                ingredient_name = ri["ingredients"]["name"]
                required_quantity = float(ri["quantity"])
                required_unit = ri["unit"]

                if recipe_id not in recipes_map:
                    recipes_map[recipe_id] = {
                        "title": recipe_title,
                        "ingredients": []
                    }

                recipes_map[recipe_id]["ingredients"].append({
                    "ingredient_id": ingredient_id,
                    "ingredient_name": ingredient_name,
                    "required_quantity": required_quantity,
                    "required_unit": required_unit
                })

            # 4. Comparar recetas con inventario
            suggested = []
            for recipe_id, recipe in recipes_map.items():
                total_ingredients = len(recipe["ingredients"])
                available_count = 0
                missing = []

                for ing in recipe["ingredients"]:
                    user_ing = inventory_map.get(ing["ingredient_id"])
                    if user_ing:
                        # TODO: Comparación de unidades real si es necesario
                        if user_ing["quantity"] >= ing["required_quantity"]:
                            available_count += 1
                        else:
                            missing.append(ing["ingredient_name"])
                    else:
                        missing.append(ing["ingredient_name"])

                match_percent = int((available_count / total_ingredients) * 100)

                suggested.append({
                    "title": recipe["title"],
                    "match_percent": match_percent,
                    "missing_ingredients": missing
                })

            # 5. Ordenar por mejor match
            suggested.sort(key=lambda x: x["match_percent"], reverse=True)

            return suggested

        except Exception as e:
            log.error(f" Error en get_suggested_recipes_by_inventory: {e}")
            return []
    
    def generate_shopping_list(self, user_uuid: str, recipe_ids: list) -> list:
        """
        Genera una lista de compras basada en recetas seleccionadas y el inventario del usuario.
        Devuelve los ingredientes faltantes y las cantidades necesarias.
        """
        try:
            # 1. Obtener inventario actual del usuario
            inventory = (
                self.sb.table("user_inventory")
                .select("ingredient_id, quantity")
                .eq("user_id", user_uuid)
                .execute()
            ).data or []

            inventory_map = {
                item["ingredient_id"]: float(item["quantity"]) for item in inventory
            }

            # 2. Obtener ingredientes requeridos para las recetas seleccionadas
            recipe_ingredients = (
                self.sb.table("recipe_ingredients")
                .select("ingredient_id, quantity, unit, ingredients(name)")
                .in_("recipe_id", recipe_ids)
                .execute()
            ).data or []

            # 3. Calcular cantidades necesarias totales por ingrediente
            shopping_needs = {}

            for ri in recipe_ingredients:
                ing_id = ri["ingredient_id"]
                name = ri["ingredients"]["name"]
                required_qty = float(ri["quantity"])
                unit = ri["unit"]

                if ing_id not in shopping_needs:
                    shopping_needs[ing_id] = {
                        "ingredient_name": name,
                        "required_quantity": 0.0,
                        "unit": unit
                    }

                shopping_needs[ing_id]["required_quantity"] += required_qty

            # 4. Comparar con inventario para calcular faltantes
            shopping_list = []

            for ing_id, data in shopping_needs.items():
                available_qty = inventory_map.get(ing_id, 0)
                to_buy = data["required_quantity"] - available_qty

                if to_buy > 0:
                    shopping_list.append({
                        "ingredient": data["ingredient_name"],
                        "quantity_to_buy": round(to_buy, 2),
                        "unit": data["unit"]
                    })

            return shopping_list

        except Exception as e:
            log.error(f" Error en generate_shopping_list: {e}")
            return []

    def get_suggested_recipes_by_expiring_ingredients(self, user_uuid: str, days_ahead: int = 3) -> list:
        """
        Sugiere recetas usando ingredientes que vencen pronto (en `days_ahead` días).
        Prioriza recetas que:
        1. Usen ingredientes con fecha más próxima de vencimiento.
        2. Tengan mayor porcentaje de match de ingredientes próximos a vencer.
        """
        try:
            today = datetime.today().date()

            # 1. Obtener inventario y filtrar por próximos a vencer
            inventory = self.get_user_inventory(user_uuid)
            expiring_items = []
            for item in inventory:
                expiry_raw = item.get("expiry_date")
                if not expiry_raw:
                    continue

                try:
                    expiry_date = datetime.strptime(expiry_raw[:10], "%Y-%m-%d").date()
                except ValueError:
                    continue

                delta_days = (expiry_date - today).days
                if 0 < delta_days <= days_ahead:
                    expiring_items.append({
                        "ingredient_id": item["ingredient_id"],
                        "ingredient_name": item["name"],
                        "expiry_date": expiry_date
                    })

            if not expiring_items:
                return []

            expiring_map = {i["ingredient_id"]: i for i in expiring_items}

            # 2. Obtener todas las recetas y sus ingredientes
            recipe_ingredients = (
                self.sb.table("recipe_ingredients")
                .select("recipe_id, ingredient_id, quantity, unit, recipes(title), ingredients(name)")
                .execute()
            ).data or []

            # 3. Agrupar por receta
            recipes_map = {}
            for ri in recipe_ingredients:
                recipe_id = ri["recipe_id"]
                recipe_title = ri["recipes"]["title"]
                ingredient_id = ri["ingredient_id"]
                ingredient_name = ri["ingredients"]["name"]

                if recipe_id not in recipes_map:
                    recipes_map[recipe_id] = {
                        "title": recipe_title,
                        "ingredients": []
                    }

                recipes_map[recipe_id]["ingredients"].append({
                    "ingredient_id": ingredient_id,
                    "ingredient_name": ingredient_name
                })

            # 4. Calcular match solo con ingredientes que vencen pronto
            suggested = []
            for recipe_id, recipe in recipes_map.items():
                total_expiring_ingredients = len(expiring_items)
                matching_expiring = [
                    ing for ing in recipe["ingredients"]
                    if ing["ingredient_id"] in expiring_map
                ]

                if not matching_expiring:
                    continue  # Saltar si la receta no usa ingredientes por vencer

                match_percent = int((len(matching_expiring) / total_expiring_ingredients) * 100)

                # Ordenar internamente por fecha de vencimiento más próxima
                closest_expiry = min(
                    expiring_map[ing["ingredient_id"]]["expiry_date"] for ing in matching_expiring
                )

                suggested.append({
                    "title": recipe["title"],
                    "match_percent": match_percent,
                    "matching_expiring_ingredients": [ing["ingredient_name"] for ing in matching_expiring],
                    "closest_expiry": closest_expiry.isoformat()
                })

            # 5. Orden final: primero por fecha más próxima, luego por % de match
            suggested.sort(key=lambda x: (x["closest_expiry"], -x["match_percent"]))

            return suggested

        except Exception as e:
            log.error(f"Error en get_suggested_recipes_by_expiring_ingredients: {e}")
            return []
