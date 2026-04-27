from app.services.usda import usda_service
from app.services.ollama import ollama_service
from app.services.openfoodfacts import openfoodfacts_service
from app.constant import LOOKUP_HUMAN_PROMPT, LOOKUP_SYSTEM_PROMPT

async def lookup_nutrition(foods: list[str]) -> dict:
    if not foods:
        return _empty_nutrition("no_foods")
    
    total = {
        "calories" : 0.0,
        "protein" : 0.0,
        "carbs" : 0.0,
        "fat" : 0.0,
        "fiber" : 0.0,
        "source" : "combined",
        "breakdown" : []   # per food item breakdown
    }

    for food in foods:
        result = await _lookup_single_food(food_name=food)
        if result:
            total["calories"] += result["calories"]
            total["protein"] += result["protein"]
            total["carbs"] += result["carbs"]
            total["fat"] += result["fat"]
            total["fiber"] += result["fiber"]
            total["breakdown"].append(result)
    
    # Round totals
    total["calories"] = round(total["calories"], 2)
    total["protein"] = round(total["protein"], 2)
    total["carbs"] = round(total["carbs"], 2)
    total["fat"] = round(total["fat"], 2)
    total["fiber"] = round(total["fiber"], 2)

    return total

async def _lookup_single_food(food_name: str) -> dict | None:
    # Step 1- USDA Search
    if usda_service.api_key:
        result = await usda_service.search_food(food_name)
        if result:
            print(f"USDA found: {food_name}")
            return result
        
    # Step 2 - fallback to openfactsfood
    result = await openfoodfacts_service.search_food(food_name)
    if result:
        print(f"OpenFoodFacts found: {food_name}")
        return result
    
    # Step 3 - fallback to Ollama estimate
    print(f"Using LLM estimate for: {food_name}")
    return await _llm_estimate(food_name)

async def _llm_estimate(food_name: str) -> dict | None:
    """
    Input: food name extracted by parser agent
    Output: Nutritional info by LLM 
    """
    prompt = LOOKUP_HUMAN_PROMPT.format(food_name=food_name)

    try:
        import json, re 
        response = await ollama_service.generate(prompt=prompt, system=LOOKUP_SYSTEM_PROMPT)

        cleaned = response.strip()
        cleaned = re.sub(r"```json|```", "", cleaned).strip()   

        data = json.loads(cleaned)

        return {
            "name" : food_name,
            "calories" : round(float(data.get("calories", 0)), 2),
            "protein" : round(float(data.get("protein", 0)), 2),
            "carbs" : round(float(data.get("carbs", 0)), 2),
            "fat" : round(float(data.get("fat", 0)), 2),
            "fiber" : round(float(data.get("fiber", 0)), 2),
            "source" : "llm_estimate"
        }
    
    except Exception as e:
        print(f"LLM estimate error for '{food_name}' : {e}")
        return None
    
def _empty_nutrition(source: str) -> dict:
    return {
        "calories" : 0.0,
        "protein" : 0.0,
        "carbs" : 0.0,
        "fat" : 0.0,
        "fiber" : 0.0,
        "source" : source,
        "breakdown" : []
    }