import httpx
import json 
from typing import List, Dict, Any 
from app.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_BASE_MODEL # or "mistral/ phi etc.. "

    async def generate(self, prompt:str, system:str = None) -> str:
        payload = {
            "model" : self.model,
            "prompt" : prompt,
            "stream": False
        }

        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                return response.json()["response"]
            except httpx.TimeoutException:
                raise Exception("Ollama timeout- is Ollama running?")
            except httpx.ConnectError:
                raise Exception("Cannot connect to Ollama - run 'ollama serve'")
            
ollama_service = OllamaService()