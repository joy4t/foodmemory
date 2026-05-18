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


RATING_PARSE_PROMPT = """Extract rating information from the user's message.
Return a JSON object with these fields:
- item_name: the dish they're rating (string)
- restaurant_name: restaurant name if mentioned (string or null)
- score: rating from 1-5 (integer)
- note: any comment about the dish (string or null)
- would_reorder: whether they'd order again based on sentiment (boolean)

If a field is unclear, make your best guess from context.
Respond with ONLY the JSON object, no other text."""


class AgentOrchestrator:
    def __init__(self):
        self.llm = LLMClient()
        self.memory = MemoryEngine()
        self.mcp = SwiggyMCPClient()

    async def process(self, user_id: str, message: str) -> dict:
        """Process a user message and return a response."""
        # Ensure user exists
        await self.memory.ensure_user(user_id)

        # Step 1: Classify intent
        intent = await self.llm.classify(INTENT_CLASSIFICATION_PROMPT, message)

        # Clean up intent
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
        search_result = await self.mcp.search_restaurants(message)
        context = json.dumps(search_result, indent=2)

        # Enrich with memory
        memory_context = ""
        for restaurant in search_result.get("restaurants", []):
            mem = await self.memory.get_restaurant_memory(user_id, restaurant["id"])
            if mem.get("ratings"):
                memory_context += f"\nUser's history at {restaurant['name']}:\n"
                for r in mem["ratings"]:
                    memory_context += f"  - {r['item_name']}: {r['score']}/5"
                    if r["note"]:
                        memory_context += f" (\"{r['note']}\")"
                    memory_context += "\n"

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
        """Show a restaurant's menu with memory overlay."""
        search_result = await self.mcp.search_restaurants(message)
        restaurants = search_result.get("restaurants", [])

        if not restaurants:
            return {
                "reply": "I couldn't find that restaurant. Could you try a different name?",
                "data": None,
            }

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
        """Add items to cart."""
        # Get global memory for context
        global_context = await self.memory.build_global_context(user_id)

        reply = await self.llm.complete_with_context(
            SYSTEM_PROMPT,
            global_context,
            f"The user wants to add items to their cart. They said: '{message}'. "
            f"Acknowledge their request, confirm what you understood they want to add, "
            f"and let them know the cart feature is being finalized.",
        )
        return {"reply": reply, "data": None}

    async def _handle_place_order(self, user_id: str, message: str) -> dict:
        """Place an order."""
        reply = await self.llm.complete(
            SYSTEM_PROMPT,
            f"The user wants to place their order. They said: '{message}'. "
            f"Let them know the ordering feature is being connected to Swiggy "
            f"and will be available soon. Be encouraging and friendly.",
        )
        return {"reply": reply, "data": None}

    async def _handle_rate_item(self, user_id: str, message: str) -> dict:
        """Handle rating a dish — parse the rating and store it."""
        # Use LLM to extract rating details
        rating_json = await self.llm.complete(RATING_PARSE_PROMPT, message)

        try:
            # Clean up potential markdown formatting
            cleaned = rating_json.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            rating_data = json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            return {
                "reply": "I'd love to save your rating! Could you tell me the dish name "
                         "and a score from 1-5? For example: 'The chicken biryani from "
                         "Meghana was amazing, 5 stars!'",
                "data": None,
            }

        item_name = rating_data.get("item_name", "Unknown dish")
        restaurant_name = rating_data.get("restaurant_name", "Unknown restaurant")
        score = rating_data.get("score", 3)
        note = rating_data.get("note")
        would_reorder = rating_data.get("would_reorder", True)

        # Find restaurant ID from name
        search_result = await self.mcp.search_restaurants(restaurant_name)
        restaurants = search_result.get("restaurants", [])
        restaurant_id = restaurants[0]["id"] if restaurants else "unknown"
        if restaurants:
            restaurant_name = restaurants[0]["name"]

        # Store the rating
        rating_id = await self.memory.quick_rate(
            user_id=user_id,
            item_name=item_name,
            restaurant_id=restaurant_id,
            restaurant_name=restaurant_name,
            score=score,
            note=note,
            would_reorder=would_reorder,
        )

        # Generate confirmation response
        stars = "⭐" * score
        reply = f"Got it! I've saved your rating:\n\n"
        reply += f"**{item_name}** at {restaurant_name}: {stars} ({score}/5)\n"
        if note:
            reply += f"Your note: \"{note}\"\n"
        if would_reorder:
            reply += f"\nI'll remember you'd order this again! "
        else:
            reply += f"\nNoted that you'd skip this next time. "
        reply += "I'll use this to give you better recommendations."

        return {
            "reply": reply,
            "data": {
                "rating_id": rating_id,
                "item_name": item_name,
                "restaurant_name": restaurant_name,
                "score": score,
            },
        }

    async def _handle_recommendation(self, user_id: str, message: str) -> dict:
        """Give food recommendations based on memory."""
        search_result = await self.mcp.search_restaurants(message)
        restaurants = search_result.get("restaurants", [])

        context = ""
        if restaurants:
            restaurant = restaurants[0]
            menu_result = await self.mcp.get_restaurant_menu(restaurant["id"])
            memory_context = await self.memory.build_memory_context(
                user_id, restaurant["id"]
            )
            # Also get global preferences
            global_context = await self.memory.build_global_context(user_id)

            context = json.dumps(menu_result, indent=2)
            if memory_context:
                context += f"\n\nMEMORY AT THIS RESTAURANT:\n{memory_context}"
            if global_context:
                context += f"\n\nOVERALL FOOD PREFERENCES:\n{global_context}"
        else:
            search_result = await self.mcp.search_restaurants("")
            global_context = await self.memory.build_global_context(user_id)
            context = json.dumps(search_result, indent=2)
            if global_context:
                context += f"\n\nOVERALL FOOD PREFERENCES:\n{global_context}"

        reply = await self.llm.complete_with_context(
            RESPONSE_WITH_RECOMMENDATION, context, message
        )

        return {"reply": reply, "data": None}

    async def _handle_general_chat(self, user_id: str, message: str) -> dict:
        """Handle general conversation."""
        reply = await self.llm.complete(GENERAL_CHAT_PROMPT, message)
        return {"reply": reply, "data": None}
