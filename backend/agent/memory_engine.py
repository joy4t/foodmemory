"""
Memory Engine — queries and updates the user's food memory.

Handles:
- Fetching past ratings for a restaurant/item
- Recording new ratings
- Tracking implicit signals (reorder frequency, skips)
- Building memory context for the LLM prompt

Will be implemented in Phase 6.
"""


class MemoryEngine:
    def __init__(self):
        pass

    async def get_restaurant_memory(self, user_id: str, restaurant_id: str) -> dict:
        """Get all memory (ratings + signals) for a user at a restaurant."""
        # TODO: Phase 6
        return {"ratings": [], "signals": []}

    async def get_item_memory(self, user_id: str, item_name: str) -> dict:
        """Get memory for a specific dish across all restaurants."""
        # TODO: Phase 6
        return {"ratings": [], "signals": []}

    async def record_rating(self, rating_data: dict) -> str:
        """Store a new rating."""
        # TODO: Phase 6
        return "not_implemented"

    async def record_signal(self, signal_data: dict) -> None:
        """Record an implicit signal (reorder, skip, etc.)."""
        # TODO: Phase 6
        pass

    async def build_memory_context(self, user_id: str, restaurant_id: str) -> str:
        """Build a text summary of the user's memory for LLM context."""
        # TODO: Phase 6
        return ""
