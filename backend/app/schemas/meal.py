from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from uuid import UUID

class MealLogRequest(BaseModel):
    text: str                       # "nasi lemak and teh tarik for lunch"
    meal_time: Optional[str] = None # breakfast, lunch, dinner
    

class NutritionData(BaseModel):
    calories: float = 0
    protein: float = 0
    carbs: float = 0 
    fat: float = 0 
    fiber: float = 0 
    source: str = "unknown"   # "usda", "openfoodfacts", "llm_estimate"

class MealLogResponse(BaseModel):
    meal_id: UUID
    raw_text: str
    parsed_food: list[str]
    nutrition: NutritionData
    meal_time: Optional[str] = None
    logged_at: datetime

    class Config: 
        from_attributes = True

class MealHistoryResponse(BaseModel):
    meals: list[MealLogResponse]
    total: int
