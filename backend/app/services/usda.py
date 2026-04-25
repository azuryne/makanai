import httpx
from app.config import settings

class USDAService:
    def __init__(self):
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.api_key = settings.USDA_API_KEY

    async def search_food(self, food_name: str) -> dict | None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try: 
                response = await client.get(
                    f"{self.base_url}/foods/search",
                    params={
                        "query":food_name,
                        "pageSize":1,
                        "dataType": "Foundation,SR Legacy"
                    }
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("foods"):
                    return None
                
                food = data["foods"][0]
                nutrients = {n["nutrientName"]: n for n in food.get("foodNutrients", [])}

                return {
                    "name" : food.get("description", food_name),
                    "calories" : self._get_nutrient(nutrients, "Energy"),
                    "protein" : self._get_nutrient(nutrients, "Protein"),
                    "carbs" : self._get_nutrient(nutrients, "Carbohydrate, by difference"),
                    "fat" : self._get_nutrient(nutrients, "Total lipid (fat)"),
                    "fiber" : self._get_nutrient(nutrients, "Fiber, total dietary"),
                    "source" : "usda"
                }
            
            except Exception as e:
                print(f"USDA error for '{food_name}': {e}")
                return None
            
    def _get_nutrient(self, nutrients:dict, name:str) -> float:
        nutrient = nutrients.get(name)
        if nutrient:
            return round(float(nutrient.get("value", 0)), 2)
        return 0.0
    
usda_service = USDAService()