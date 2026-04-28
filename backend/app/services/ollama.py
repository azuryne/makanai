"""
Ollama services wrapper for Makanai

Handles all communication with the local Ollama instance.
Supports both regular and streaming generation

Endpoints used:
    POST /api/generate  -> regular response
    POST /api/generate (streaming) -> streaming response
"""

import httpx
import json 
from typing import List, Dict, Any 
from app.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_BASE_MODEL # or "mistral/ phi etc.. "

    async def generate(self, prompt:str, system:str = None) -> str:
        """
        Generate a complete response from Ollama.

        Waits for the full response before returning.
        Used by parser, lookup and insight agents where
        we need the complete output to parse as JSON.

        Args:
            prompt: the user prompt
            system: optional system prompt

        Returns:
            complete response string

        Raises:
            Exception if Ollama is not running or times out
        """
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
            
    async def stream(self, prompt:str, system:str = None) -> str:
        """
        Stream response token from Ollama one by one

        Yields each token as it arrives instead of waiting
        for the full response. Used by the chat agent to 
        provide a ChatGPT like typing effect

        Args:
            prompt: the user prompt
            system: optional system prompt

        Yields:
            individual token strings as they arrive

        Raises:
            Exception if Ollama is not running or times out
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }

        if system:
            payload["system"] = system 
            
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                token = data.get("response", "")
                                done = data.get("done", False)

                                if token:
                                    yield token

                                if done:
                                    break

                            except json.JSONDecodeError:
                                continue

            except httpx.TimeoutException:
                raise Exception("Ollama stream timeout - is Ollama running?")
            
            except httpx.ConnectError:
                raise Exception("Cannot connect to Ollama - run 'Ollama serve")
            
ollama_service = OllamaService()