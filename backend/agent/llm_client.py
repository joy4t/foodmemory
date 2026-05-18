"""
LLM Client — wraps Groq API.

Designed to be swappable: change this file to switch providers
without touching any business logic.
"""

from groq import Groq
from backend.config import settings


class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL

    async def complete(self, system_prompt: str, user_message: str) -> str:
        """Send a message to the LLM and return the response."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    async def classify(self, system_prompt: str, user_message: str) -> str:
        """Classify user intent — low temperature for consistency."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,
            max_tokens=50,
        )
        return response.choices[0].message.content.strip().lower()

    async def complete_with_context(
        self, system_prompt: str, context: str, user_message: str
    ) -> str:
        """Send a message with additional context (memory, menu data, etc.)."""
        full_message = f"""CONTEXT:
{context}

USER MESSAGE:
{user_message}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_message},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
