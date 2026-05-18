"""
Agent Orchestrator — the brain of FoodMemory.

Takes a user message, classifies intent, calls the right tools
(MCP, memory engine, LLM), and returns a contextual response.
"""

import json
from backend.agent.llm_client import LLMClient
from backend.agent.memory_engine import MemoryEngine
from backend.agent.prompts import (
    INTENT_CLASSIFICATION_PROMPT,
    RESPONSE_WITH_RESTAURANTS,
    RESPONSE_WITH_MENU,
    RESPONSE_WITH_RECOMMENDATION,
    GENERAL_CHAT_PROMPT,
    SYSTEM_PROMPT,
)
from backend.mcp.client import SwiggyMCPClient


class AgentOrchestrator:
    def __init__(self):
        self.llm = LLMClient()
        self.memory = MemoryEngine()
        self.mcp = SwiggyMCPClient()

    async def process(self, user_id: str, message: str) -> dict:
        """Process a user message and return a response."""

        # Step 1: Classify intent
        intent = await self.llm.classify(INTENT_CLASSIFICATION_PROMPT, message)

        # Clean up intent — LLM might return extra text
        valid_intents = [
            "search_restaurant",
            "browse_menu",
            "add_to_cart",
            "place_order",
            "rate_item",
            "ask_recommendation",
            "general_chat",
        ]
        if intent not in valid_intents:
            # Try to find a valid intent in the response
            for vi in valid_intents:
                if vi in intent:
                    intent = vi
                    break
            else:
                intent = "general_chat"

        # Step 2: Route to handler
        handler = {
            "search_restaurant": self._handle_search_restaurant,
            "browse_menu": self._handle_browse_menu,
            "add_to_cart": self._handle_add_to_cart,
            "place_order": self._handle_place_order,
            "rate_item": self._handle_rate_item,
            "ask_recommendation": self._handle_recommendation,
            "general_chat": self._handle_general_chat,
        }

        handler_fn = handler.get(intent, self._handle_general_chat)
        result = await handler_fn(user_id, message)
        result["intent"] = intent
        return result

    async def _handle_search_restaurant(self, user_id: str, message: str) -> dict:
        """Search for restaurants based on user query."""
        # Extract search query from message
        search_result = await self.mcp.search_restaurants(message)

        # Build context with restaurant data
        context = json.dumps(search_result, indent=2)

        # Get memory context for these restaurants
        memory_context = ""
        for restaurant in search_result.get("restaurants", []):
            mem = await self.memory.get_restaurant_memory(
                user_id, restaurant["id"]
            )
            if mem.get("ratings"):
                memory_context += (
                    f"\nUser's history at {restaurant['name']}: {mem}\n"
                )

        full_context = context
        if memory_context:
            full_context += f"\n\nUSER'S FOOD MEMORY:\n{memory_context}"

        reply = await self.llm.complete_with_context(
            RESPONSE_WITH_RESTAURANTS, full_context, message
        )

        return {
            "reply": reply,
            "data": {"restaurants": search_result.get("restaurants", [])},
        }

    async def _handle_browse_menu(self, user_id: str, message: str) -> dict:
        """Show a restaurant's menu."""
        # Try to find which restaurant the user means
        search_result = await self.mcp.search_restaurants(message)
        restaurants = search_result.get("restaurants", [])

        if not restaurants:
            return {
                "reply": "I couldn't find that restaurant. Could you try a different name?",
                "data": None,
            }

        # Use the first matching restaurant
        restaurant = restaurants[0]
        menu_result = await self.mcp.get_restaurant_menu(restaurant["id"])

        # Get memory for this restaurant
        memory_context = await self.memory.build_memory_context(
            user_id, restaurant["id"]
        )

        context = json.dumps(menu_result, indent=2)
        if memory_context:
            context += f"\n\nUSER'S FOOD MEMORY:\n{memory_context}"

        reply = await self.llm.complete_with_context(
            RESPONSE_WITH_MENU, context, message
        )

        return {
            "reply": reply,
            "data": {
                "restaurant": restaurant,
                "menu": menu_result.get("menu_items", []),
            },
        }

    async def _handle_add_to_cart(self, user_id: str, message: str) -> dict:
        """Add items to cart. For now, acknowledge and guide."""
        reply = await self.llm.complete(
            SYSTEM_PROMPT,
            f"The user wants to add items to their cart. They said: '{message}'. "
            f"Acknowledge their request, confirm what you understood they want to add, "
            f"and let them know the cart feature is being set up. "
            f"Ask them to confirm the items and quantities.",
        )
        return {"reply": reply, "data": None}

    async def _handle_place_order(self, user_id: str, message: str) -> dict:
        """Place an order. For now, acknowledge."""
        reply = await self.llm.complete(
            SYSTEM_PROMPT,
            f"The user wants to place their order. They said: '{message}'. "
            f"Let them know the ordering feature is being connected to Swiggy "
            f"and will be available soon. Be encouraging and friendly.",
        )
        return {"reply": reply, "data": None}

    async def _handle_rate_item(self, user_id: str, message: str) -> dict:
        """Handle rating a dish."""
        reply = await self.llm.complete(
            SYSTEM_PROMPT,
            f"The user wants to rate a dish. They said: '{message}'. "
            f"Acknowledge their rating enthusiastically. Ask for a 1-5 star score "
            f"if they didn't provide one, and ask for a short note about the dish. "
            f"Let them know you'll remember this for next time.",
        )
        return {"reply": reply, "data": None}

    async def _handle_recommendation(self, user_id: str, message: str) -> dict:
        """Give food recommendations based on memory."""
        # Try to identify which restaurant
        search_result = await self.mcp.search_restaurants(message)
        restaurants = search_result.get("restaurants", [])

        context = ""
        if restaurants:
            restaurant = restaurants[0]
            menu_result = await self.mcp.get_restaurant_menu(restaurant["id"])
            memory_context = await self.memory.build_memory_context(
                user_id, restaurant["id"]
            )
            context = json.dumps(menu_result, indent=2)
            if memory_context:
                context += f"\n\nUSER'S FOOD MEMORY:\n{memory_context}"
        else:
            # General recommendation — search popular
            search_result = await self.mcp.search_restaurants("")
            context = json.dumps(search_result, indent=2)

        reply = await self.llm.complete_with_context(
            RESPONSE_WITH_RECOMMENDATION, context, message
        )

        return {"reply": reply, "data": None}

    async def _handle_general_chat(self, user_id: str, message: str) -> dict:
        """Handle general conversation."""
        reply = await self.llm.complete(GENERAL_CHAT_PROMPT, message)
        return {"reply": reply, "data": None}
