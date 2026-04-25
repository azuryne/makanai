import httpx
from typing import Dict, Any, Optional

class OpenFoodFactsService:
    def __init__(self):
        self.base_url = "https://world.openfoodfacts.org"

    async def search_food(self, food_name:str) -> Optional[Dict[str, Any]]:
        """Search for a food product and return nutrition data"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/cgi/search.pl",
                                            params={
                                                "search_terms" : food_name,
                                                "json" : 1,
                                                "page_size" : 1,
                                                "fields" : "product_name,nutriments"
                                            })
                response.raise_for_status()
                data = response.json()
                
                products = data.get("products", [])
                if not products:
                    return None

                product = products[0]
                nutriments = product.get("nutriments", {})

                return {
                    "name" : product.get("product_name", food_name),
                    "calories" : round(float(nutriments.get("energy-kcal_100g", 0)), 2),
                    "protein" : round(float(nutriments.get("protein_100g", 0)), 2),
                    "carbs" : round(float(nutriments.get("carbohydrates_100g", 0)), 2),
                    "fat" : round(float(nutriments.get("fat_100g", 0)), 2),
                    "fiber" : round(float(nutriments.get("fiber_100g", 0)), 2),
                    "source" : "openfoodfacts"
                }

            except Exception as e:
                print(f"OpenFoodFacts error for '{food_name} : {e}")
                return None                
                 
openfoodfacts_service = OpenFoodFactsService()