"""
Insight Agent for MAKANAI

Analyzes a user's weekly meal logs to generate personalized mindful eating
insights powered by Ollama. 

Responsibilities:
    - Calculates average daily nutrition from meal logs
    - Builds a structured prompt with meal history
    - Calls Ollama to generate insights and suggestions
    - Returns structured insight data

Called by: 
    orchestrator.orchestrate_weekly_insight()
"""

from app.services.ollama import ollama_service
import re
import json
import logging 
from app.constant import INSIGHT_SYSTEM_PROMPT, INSIGHT_HUMAN_PROMPT

logger = logging.getLogger(__name__)

async def generate_weekly_insight(meals: list[dict]) -> dict:
    """
    Generate a weekly insight summary from meal history.

    Takes a list of meals records from the database,
    calculates nutrition averages, then calls Ollama
    to generate a natural languange summary 

    Args:
        meals: list of meal dicts from the database
               each dict has parsed_foods and nutrition keys

    Returns:
        dict with summary, highlights, suggestions,
        and average_nutrition values
    """

    # Calculates nutrition averages
    averages = _calculate_averages(meals)

    # Build meal summary for the prompt
    meal_summary = _build_meal_summary(meals)

    # Build prompt
    prompt = INSIGHT_HUMAN_PROMPT.format(
        meal_summary=meal_summary,
        calories=averages["calories"],
        protein=averages["protein"],
        carbs=averages["carbs"],
        fat=averages["fat"],
        fiber=averages["fiber"],
        total_meals=len(meals)
    )

    try: 
        response = await ollama_service.generate(
            prompt=prompt, 
            system=INSIGHT_SYSTEM_PROMPT
        )

        # clean and parse response
        cleaned = response.strip()
        cleaned = re.sub(r"```json|```", "", cleaned).strip()

        data = json.loads(cleaned)

        return {
            "summary" : data.get("summary", "Great job logging your meals this week!"),
            "highlights" : data.get("highlights", []),
            "suggestions" : data.get("suggestions", []),
            "average_nutrition" : averages
        }
    
    except json.JSONDecodeError:
        print(f"Insight agent JSON error, raw response: {response}")
        return _fallback_insight(averages, len(meals))
    
    except Exception as e:
        print(f"Insight agent error: {e}")
        return _fallback_insight(averages, len(meals))
    
def _calculate_averages(meals: list[dict]) -> dict:
    """
    Calculate average daily nutrition from meal list.

    Args:
        meals: list of meal dicts with nutrition key 

    Returns: 
        dict of average nutrition values rounded to 2dp
    
    """
    if not meals: 
        return {
            "calories" : 0.0,
            "protein" : 0.0,
            "carbs" : 0.0,
            "fat" : 0.0,
            "fiber" : 0.0
        }
    
    total = {
        "calories": 0.0,
        "protein" : 0.0,
        "carbs" : 0.0,
        "fat" : 0.0,
        "fiber": 0.0
    }

    valid_meals = 0
    for meal in meals: 
        nutrition  = meal.get("nutrition", {})
        if nutrition:
            total["calories"] += float(nutrition.get("calories", 0))
            total["protein"] += float(nutrition.get("protein", 0))
            total["carbs"] += float(nutrition.get("carbs", 0))
            total["fat"] += float(nutrition.get("fat", 0))
            total["fiber"] += float(nutrition.get("fiber", 0))
            valid_meals += 1

    if valid_meals == 0:
        return total
    
    # Average over 7 days not just meal count 

    days = 7
    return {
        "calories" : round(total["calories"] / days, 2),
        "protein" : round(total["protein"] / days, 2),
        "carbs" : round(total["carbs"] / days, 2),
        "fat" : round(total["fat"] / days, 2),
        "fiber" : round(total["fiber"] / days, 2)
    }

def _build_meal_summary(meals: list[dict]) -> str:
    """
    Build a readable meal summary string for the prompt.

    Formates each meal into a readable line so Ollama
    can understand what the user has been eatingh 

    Args:
        meals: list of meal dicts

    Returns:
        formatted string of meal history
    """
    if not meals:
        return "No meals logged this week"
    
    lines = []
    for i, meal in enumerate(meals, 1):
        foods = meal.get("parsed_foods", [])
        meal_time = meal.get("meal_time", "unspecified")
        nutrition = meal.get("nutrition", {})
        calories = nutrition.get("calories", 0)

        food_str = ", ".join(foods) if foods else meal.get("raw_text", "unknown")
        lines.append(
            f"{i}. {meal_time.capitalize()}: {food_str} "
            f"({round(calories)} kcal)"
        )
    
    return "\n".join(lines)

def _fallback_insight(averages: dict, total_meals: int) -> dict:
    """
    Fallback insight when Ollama fails or returns invalid JSON

    Returns a simple generic insight so the API never 
    fails completely even if Ollama is unavailable.

    Args:
        averages: calculated nutrition averages
        total_meals: number of meals logged 

    Returns:
        dict with basic insight data
    """

    return { 
        "summary" : (
            f"You logged {total_meals} meals this week",
            f"Your average daily intake was "
            f"{averages['calories']} calories, "
            f"{averages['protein']}g protein, "
            f"{averages['carbs']}g carbs and "
            f"{averages['fat']}g fat. Keep it up!"
        ),
        "highlights": [
            "You are actively tracking your meals",
            "Consistency is key to healthy eating"
        ],
        "suggestions": [
            "Try to log all meals for a more accurate insight",
            "Aim for at least 25g of fiber daily"
        ],
        "average_nutrition": averages
    }


