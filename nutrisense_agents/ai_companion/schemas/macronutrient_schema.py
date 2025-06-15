from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class MacronutrientExtraction(BaseModel):
    """Schema para la extracción de macronutrientes de ingredientes"""
    
    # Información básica del alimento
    name: str = Field(description="Nombre del alimento/ingrediente principal")
    description: Optional[str] = Field(description="Descripción del alimento", default=None)
    brand: Optional[str] = Field(description="Marca del producto si aplica", default=None)
    
    # Macronutrientes por 100g
    calories_per_100g: float = Field(description="Calorías por 100 gramos")
    protein_per_100g: float = Field(description="Proteínas en gramos por 100g")
    carbs_per_100g: float = Field(description="Carbohidratos en gramos por 100g")
    fat_per_100g: float = Field(description="Grasas en gramos por 100g")
    fiber_per_100g: Optional[float] = Field(description="Fibra en gramos por 100g", default=None)
    sugar_per_100g: Optional[float] = Field(description="Azúcares en gramos por 100g", default=None)
    sodium_per_100g: Optional[float] = Field(description="Sodio en miligramos por 100g", default=None)
    
    # Cantidad estimada consumida
    estimated_quantity_grams: float = Field(description="Cantidad estimada consumida en gramos")
    
    # Macronutrientes totales consumidos
    total_calories: float = Field(description="Calorías totales consumidas")
    total_protein: float = Field(description="Proteínas totales consumidas en gramos")
    total_carbs: float = Field(description="Carbohidratos totales consumidos en gramos")
    total_fat: float = Field(description="Grasas totales consumidas en gramos")
    total_fiber: Optional[float] = Field(description="Fibra total consumida en gramos", default=None)
    total_sugar: Optional[float] = Field(description="Azúcares totales consumidos en gramos", default=None)
    total_sodium: Optional[float] = Field(description="Sodio total consumido en miligramos", default=None)
    
    # Información adicional
    category: Optional[str] = Field(description="Categoría del alimento (fruta, verdura, proteína, etc.)", default=None)
    preparation_method: Optional[str] = Field(description="Método de preparación si es relevante", default=None)
    confidence_score: float = Field(description="Nivel de confianza en la extracción (0.0 a 1.0)", default=0.8)

class FoodDiaryEntry(BaseModel):
    """Schema para entrada en el diario alimentario"""
    
    user_id: str = Field(description="ID del usuario")
    meal_type: str = Field(description="Tipo de comida (desayuno, almuerzo, cena, snack)")
    consumed_at: datetime = Field(description="Fecha y hora de consumo")
    
    # Totales de la comida completa
    total_calories: float = Field(description="Calorías totales de la comida")
    total_protein: float = Field(description="Proteínas totales en gramos")
    total_carbs: float = Field(description="Carbohidratos totales en gramos")
    total_fat: float = Field(description="Grasas totales en gramos")
    total_fiber: Optional[float] = Field(description="Fibra total en gramos", default=None)
    total_sugar: Optional[float] = Field(description="Azúcares totales en gramos", default=None)
    total_sodium: Optional[float] = Field(description="Sodio total en miligramos", default=None)
    
    notes: Optional[str] = Field(description="Notas adicionales", default=None)

class FoodPhotoAnalysis(BaseModel):
    """Schema para análisis de foto de comida"""
    
    food_diary_id: str = Field(description="ID de la entrada del diario alimentario")
    photo_url: str = Field(description="URL de la foto analizada")
    analysis_confidence: float = Field(description="Confianza en el análisis de la foto")
    detected_foods: List[str] = Field(description="Lista de alimentos detectados en la foto")
    analysis_notes: Optional[str] = Field(description="Notas del análisis", default=None)

class Gender(str, Enum):
    """Gender options for nutritional calculations"""
    MALE = "male"
    FEMALE = "female"

class ActivityLevel(str, Enum):
    """Activity level for BMR calculations"""
    SEDENTARY = "sedentary"          # Little to no exercise
    LIGHTLY_ACTIVE = "lightly_active"  # Light exercise 1-3 days/week
    MODERATELY_ACTIVE = "moderately_active"  # Moderate exercise 3-5 days/week
    VERY_ACTIVE = "very_active"      # Hard exercise 6-7 days/week
    EXTRA_ACTIVE = "extra_active"    # Very hard exercise, physical job

class Goal(str, Enum):
    """Nutritional goals for macro distribution"""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    ENDURANCE = "endurance"
    STRENGTH = "strength"

class UserNutritionalProfile(BaseModel):
    """User nutritional profile for contextualized analysis"""
    
    # Basic demographics
    age: int = Field(description="Age in years", ge=10, le=120)
    gender: Gender = Field(description="Gender for BMR calculations")
    weight_kg: float = Field(description="Current weight in kilograms", gt=0)
    height_cm: float = Field(description="Height in centimeters", gt=0)
    
    # Activity and goals
    activity_level: ActivityLevel = Field(description="Physical activity level")
    goal: Goal = Field(description="Primary nutritional goal")
    
    # Optional additional info
    body_fat_percentage: Optional[float] = Field(description="Body fat percentage if known", default=None, ge=5, le=50)
    medical_conditions: Optional[List[str]] = Field(description="Relevant medical conditions", default=None)
    dietary_restrictions: Optional[List[str]] = Field(description="Dietary restrictions or preferences", default=None)

class NutritionalCalculations(BaseModel):
    """Calculated nutritional values based on user profile"""
    
    # Weight calculations
    ideal_weight_kg: float = Field(description="Ideal weight using Lorentz formula")
    weight_difference_kg: float = Field(description="Difference from ideal weight (positive = overweight)")
    
    # Metabolic calculations
    bmr_calories: float = Field(description="Basal Metabolic Rate using Harris-Benedict")
    vct_calories: float = Field(description="Total daily calorie expenditure (VCT)")
    
    # Macro targets
    target_protein_g: float = Field(description="Target protein in grams")
    target_carbs_g: float = Field(description="Target carbohydrates in grams")
    target_fat_g: float = Field(description="Target fat in grams")
    
    # Percentages
    protein_percentage: float = Field(description="Protein percentage of total calories")
    carbs_percentage: float = Field(description="Carbs percentage of total calories")
    fat_percentage: float = Field(description="Fat percentage of total calories")

class ContextualizedAnalysis(BaseModel):
    """Contextualized analysis of the food intake"""
    
    # Percentage of daily targets met
    calories_vs_target_percent: float = Field(description="Calories as percentage of daily target")
    protein_vs_target_percent: float = Field(description="Protein as percentage of daily target")
    carbs_vs_target_percent: float = Field(description="Carbs as percentage of daily target")
    fat_vs_target_percent: float = Field(description="Fat as percentage of daily target")
    
    # Alignment with goals
    alignment_score: float = Field(description="How well this food aligns with user goals (0-10)", ge=0, le=10)
    
    # Recommendations
    recommendations: List[str] = Field(description="Personalized recommendations based on intake and profile")
    warnings: Optional[List[str]] = Field(description="Warnings if any macros are excessive", default=None)
    
    # Goal-specific insights
    goal_specific_notes: str = Field(description="Notes specific to the user's goal")

class ContextualizedMacronutrientExtraction(BaseModel):
    """Enhanced macronutrient extraction with user context and analysis"""
    
    # Original extraction data
    food_extraction: MacronutrientExtraction = Field(description="Basic food extraction data")
    
    # User context
    user_profile: Optional[UserNutritionalProfile] = Field(description="User nutritional profile", default=None)
    nutritional_calculations: Optional[NutritionalCalculations] = Field(description="Calculated nutritional targets", default=None)
    
    # Contextualized analysis
    contextualized_analysis: Optional[ContextualizedAnalysis] = Field(description="Analysis in user context", default=None)
    
    # Metadata
    analysis_timestamp: datetime = Field(description="When the analysis was performed", default_factory=datetime.now)
    mode: str = Field(description="Analysis mode (local or full)", default="local")
