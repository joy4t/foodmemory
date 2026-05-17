"""
Swiggy MCP Client — interface for calling Swiggy's Food MCP tools.

In mock mode, returns data from mock_responses.py.
In staging/production, calls the real MCP server.

Will be fully implemented in Phase 3 (mock) and post-SBC approval (real).
"""

from backend.config import settings
from backend.mcp.mock_responses import MockMCP


class SwiggyMCPClient:
    def __init__(self):
        self.mode = settings.SWIGGY_MCP_MODE
        if self.mode == "mock":
            self._mock = MockMCP()

    async def search_restaurants(self, query: str, location: str = "Bangalore") -> dict:
        if self.mode == "mock":
            return self._mock.search_restaurants(query)
        # TODO: Real MCP call
        raise NotImplementedError("Real MCP not yet configured")

    async def get_restaurant_menu(self, restaurant_id: str) -> dict:
        if self.mode == "mock":
            return self._mock.get_restaurant_menu(restaurant_id)
        raise NotImplementedError("Real MCP not yet configured")

    async def search_menu(self, query: str) -> dict:
        if self.mode == "mock":
            return self._mock.search_menu(query)
        raise NotImplementedError("Real MCP not yet configured")

    async def update_food_cart(self, items: list) -> dict:
        if self.mode == "mock":
            return self._mock.update_food_cart(items)
        raise NotImplementedError("Real MCP not yet configured")

    async def place_food_order(self, cart_id: str) -> dict:
        if self.mode == "mock":
            return self._mock.place_food_order(cart_id)
        raise NotImplementedError("Real MCP not yet configured")
