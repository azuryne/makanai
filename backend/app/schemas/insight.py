"""
Pydantic schema for weekly insight responses.

Uses by:
    GET /api/insights/weekly
"""

from pydantic import BaseModel
from datetime import date

class NutritionAverage(BaseModel):
    """
    Represent average daily nutrition for the week

    All values are per day averages calculated from 
    the user's meal logs over the past 7 days

    """
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    fiber: float = 0.0

class WeeklyInsightResponse(BaseModel):
    """
    Full weekly insights response to the front-end

    Contains AI-generated summary, nutrition averages,
    highlihts and actionable suggestions

    Fields:
        week_start -> start date of the insight period
        week_end -> end date of the insight period
        total_meals -> number of meals logged this week 
        average_nutrition -> daily average nutrition values
        summary -> AI generated paragraph summary
        highlights -> list of positive eating habits
        suggestions -> list of improvement suggestions
    """

    week_start: date
    week_end: date 
    total_meals: int
    average_nutrition: NutritionAverage
    summary: str
    highlights: list[str]
    suggestions: list[str]


