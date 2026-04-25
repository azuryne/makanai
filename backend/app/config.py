from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # Database 
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_BASE_MODEL: str = "llama2"

    # USDA
    USDA_API_KEY: str = os.getenv("USDA_API_KEY")

    # App
    APP_ENV: str = "development"

    model_config = {
        "env_file" :  ".env",
        "env_file_encoding" : "utf-8",
        "extra" : "ignore"
    }

@lru_cache()
def get_settings() -> Settings:  # settings are only loaded once — not on every request
    return Settings()

settings = get_settings()