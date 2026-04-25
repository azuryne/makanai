"""
Orchestrator for MAKANAI

Coordinates all agents and services in the correct order.
Acts as the middle layer between API routes and agents

Functions:
    orchestrate_meal_log() -> handles meal logging flow
    orchestrate_weekly_insight() -> handles weekly insight flow
    orchestrate_chat() -> handles chatbot flow
"""


from app.agents.parser_agent import parse_foods
from app.agents.lookup_agent import lookup_nutrition

async def orchestrate_meal_log(text: str) -> dict:
    """
    Main orchestrator for logging a meal
    Step 1 - Parse food item from raw text
    Step 2 - Lookup nutrition for each food item
    Step 3 - Return combined result    
    """
    print(f"Orchestrator: processing '{text}'")

    # Step 1 - parse food items from text using Ollam 
    parsed_foods = await parse_foods(text)
    print(f"Parsed foods: {parsed_foods}")

    if not parsed_foods:
        return {
            "parsed_foods" : [],
            "nutrition" : {
                "calories" : 0.0,
                "protein" : 0.0,
                "carbs" : 0.0,
                "fat" : 0.0,
                "fiber" : 0.0,
                "source" : "no_food_detected",
                "breakdown" : []
            }
        }
    
    # Step 2 - lookup nutrition for each food
    nutrition = await lookup_nutrition(parsed_foods)
    print(f"Nutrition results: {nutrition}")

    return {
        "parsed_foods" : parsed_foods,
        "nutrition" : nutrition
    }

async def orchestrate_weekly_insights(
        user_id: str,
        meals: list[dict]
) -> dict:
    """
    Orchestrator for generating weekly insight summary.
    Called by: GET /api/insights/weekly

    Flow:
        1. Validates meal list is not empty
        2. Insight Agent -> analyze meal history via Ollama
        3. Returns structured insight data

    Args:
        user_id: current user's UUID as string
        meals: list of meal dicts from the database
               each dict has keys:
               - raw_text
               - parsed_foods
               - nutrition
               - meal_time
               - logged_at    

    Returns: 
        dict with summary, highlights, suggestions, 
        and average_nutrition values
    """

    print(f"Orchestrator: generating weekly insights for user {user_id}")

    # Import here to avoid circular import 
    from app.agents.insight_agent import generate_weekly_insight

    # Guard - no meals logged this week 
    if not meals:
        print("No meals found for this week")
        return {
            "summary": (
                "No meals were logged this week",
                "Start logging your meals to get personalized insights !"
            ),
            "highlights" : [],
            "suggestions" : [
                "Try logging at least 3 meals a day",
                "Include breakfast for a more complete picture"
            ],
            "average_nutrition": {
                "calories" : 0.0,
                "protein" : 0.0,
                "carbs" : 0.0,
                "fat" : 0.0,
                "fiber" : 0.0
            }
        }

    # Run insight agent
    insight = await generate_weekly_insight(meals)
    print(f"Weekly insight generated for {len(meals)} meals")

    return insight


# TODO: orchestrator for chatbot

# async def orchestrate_chat
