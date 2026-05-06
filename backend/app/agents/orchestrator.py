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
    Orchestrator for logging a meal
    Called by: POST /api/meals/log

    Flow: 
        1. Parser Agent -> extract food items from text via Ollama
        2. Lookup Agent -> fetch nutrition from USDA / Open Food Source / Ollama

    Args:
        text: raw meal text from user (e.g: nasi lemak for lunch)
    
    Returns:
        dict with parsed_foods list and nutrition list 
    """
    print(f"Orchestrator: processing '{text}'")

    # Step 1 - parse food items from text using Ollam 
    parsed_foods = await parse_foods(text)
    print(f"Parsed foods: {parsed_foods}")

    if not parsed_foods:
        return {
            "parsed_foods" : [],
            "nutrition" : _empty_nutrition("no_foods_detected")
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
    from app.agents.insight_agent import generate_weekly_insights

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
    insight = await generate_weekly_insights(meals)
    print(f"Weekly insight generated for {len(meals)} meals")

    return insight

# TODO: orchestrator for chatbot

async def orchestrate_chat(
        user_id: str,
        message: str,
        meal_history: list[dict],
        chat_history: list[dict]
) -> dict:
    """
    Orchestrator for chatbot messages. 
    Called by POST /api/chat 

    Flow:
        1. Context builder -> build prompt with user's meal history
        2. Chat Agent      -> generate response via Ollama

    Args:
        user_id: current user's UUID as string
        message: user's chat message
        meal_hisory: recent meals from DB context 
        chat_history: previous chat message for context
    
    Returns: 
        dict with reply string and context_used count    
    """
    print(f"Orchestrator: processing chat for user {user_id}")
    
    # Import here to avoid circular import 
    from app.agents.chat_agent import generate_chat_response
    from app.services.context_builder import build_chat_context

    # Step 1 - build context from history 
    context = build_chat_context(
        meal_history=meal_history,
        chat_history=chat_history
    )

    # Step 2 - generate chat response 
    response = await generate_chat_response(
        message=message,
        context=context
    )
    print(f"Chat response generated")

    return {
        "reply": response, 
        "context_used" : len(meal_history)
    }

def _empty_nutrition(source: str) -> dict:
    """
    Helper that returns an empty nutrition dict 

    Used as fallback when no foods are detected 
    or when nutrition lookup fails completely
    
    Args:
        source: string describing why nutrition is empty

    Returns:
        dict with all nutrition values set to 0 
    """
    return {
        "calories" : 0.0,
        "protein" : 0.0,
        "carbs" : 0.0, 
        "fat" : 0.0,
        "fiber" : 0.0,
        "source" : source,
        "breakdown" : []
    }




