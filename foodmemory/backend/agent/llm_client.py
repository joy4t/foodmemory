"""
LLM Client — wraps Groq API.

Designed to be swappable: change this file to switch providers
without touching any business logic.

Will be implemented in Phase 4.
"""

from backend.config import settings


class LLMClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.LLM_MODEL

    async def complete(self, system_prompt: str, user_message: str) -> str:
        """Send a message to the LLM and return the response."""
        # TODO: Phase 4 — wire up Groq SDK
        return "LLM client not yet implemented"
