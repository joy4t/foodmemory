import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/food_memory.db")
    SWIGGY_MCP_MODE: str = os.getenv("SWIGGY_MCP_MODE", "mock")
    SWIGGY_MCP_URL: str = os.getenv("SWIGGY_MCP_URL", "")


settings = Settings()
