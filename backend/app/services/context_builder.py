"""
Context Builder for MAKANAI chatbot.

Builds a structured prompt context string from the user's 
meal history and chat history so Ollama understands
what the user has been eating and what was discussed.

Called by:
    orchestrator.orchestrate_chat()
"""

def build_chat_context(
        meal_history: list[dict],
        chat_history: list[dict]
) -> str:
    """
    Build a formatted context string for the chat prompt

    Combines meal history and chat history into a readable 
    string that gets injected into the Ollama prompt so 
    the chatbot knows about the user's eating habits.

    Args:
        meal_history: list of recent meal dicts from DB
                      each has parsed_foods, nutrition, meal_time
        chat_history: list of recent chat message dicts from DB
                      each has role and message 
    
    Returns:
        formatted context string ready to inject into prompt
    """

    context_parts = []

    # Build meal history context 
    meal_context = _build_meal_context(meal_history)
    if meal_context:
        context_parts.append(meal_context)
    
    # Build chat history context 
    chat_context = _build_chat_history_context(chat_history)
    if chat_context:
        context_parts.append(chat_context)
    
    if not context_parts:
        return "The user has no meal history yet"
    
    return "\n\n".join(context_parts)


def _build_meal_context(meals: list[dict]) -> str:
    """
    Format meal history into a readable string 

    Args:
        meals: list of meal dicts

    Returns:
        formatted meal history string
    """

    if not meals:
        return ""
    
    lines = ["User's recent meals:"]

    for meal in meals:
        foods = meal.get("parsed_foods", [])
        meal_time = meal.get("meal_time") or "unspecified"
        nutrition = meal.get("nutrition", {})
        calories = round(float(nutrition.get("calories", 0)))
        protein = round(float(nutrition.get("protein", 0)))
        carbs = round(float(nutrition.get("carbs", 0)))
        fat = round(float(nutrition.get("fat", 0)))
        logged_at = meal.get("logged_at", "")

        food_str = ", ".join(foods) if foods else "unknown"

        lines.append(
            f"= {meal_time.capitalize()}: {food_str} "
            f"| {calories} kcal, {protein}g protein, "
            f"{carbs}g carbs, {fat}g fat"
            f"{' (' + logged_at[:10] + ')' if logged_at else ''}"
        )
    
    return "\n".join(lines)

def _build_chat_history_context(chat_history: list[dict]) -> str:
    """
    Format recent chat history into a readable string.

    Includes the last few messages so Ollama can maintain 
    conversation continuity and not repeat itself

    Args:
        chat_history: list of chat message dicts

    Returns:
        formatted chat history string
    
    """

    if not chat_history:
        return ""
    
    lines = ["Previous conversation:"]
    
    for msg in chat_history:
        role = msg.get("role", "user")
        message = msg.get("message", "")
        prefix = "User" if role == "user" else "MAKANAI"
        lines.append(f"{prefix}: {message}")

    return "\n".join(lines)




