import json 
import re 
from app.services.ollama import ollama_service
from app.constant import PARSER_HUMAN_PROMPT, PARSER_SYSTEM_PROMPT

async def parse_foods(text: str) -> list[str]:
    """
    Input: User text 
    Output: Food item from user text

    Job: Extract food item from messy human text
    """
    prompt = PARSER_HUMAN_PROMPT.format(text=text)

    try:
        response = await ollama_service.generate(
            prompt=prompt,
            system=PARSER_SYSTEM_PROMPT
        )

        # Clean response - remove markdown code block if present 
        cleaned = response.strip()
        cleaned = re.sub(r"```json|```", "", cleaned).strip()

        # Parse JSON 
        foods = json.loads(cleaned)

        # Ensure its a list of str
        if isinstance(foods, list):
            return [str(f).lower().strip() for f in foods]
        
        return []
    
    except json.JSONDecodeError:
        # Fallback - return raw text as single item if JSON fails
        print(f"Parser agent JSON error, raw response: {response}")
        return [text.strip()]
    
    except Exception as e:
        print(f"Parser agent error: {e}")
        return []
