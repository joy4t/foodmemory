"""
Mock MCP Responses — realistic fake data mirroring Swiggy's API shapes.

This module returns data in the exact structure Swiggy's MCP tools would return,
so swapping to real APIs later requires zero changes in business logic.
"""

import uuid
from datetime import datetime


class MockMCP:
    """Mock Swiggy MCP server with realistic Bangalore restaurant data."""

    def __init__(self):
        self._restaurants = {
            "rest_001": {
                "id": "rest_001",
                "name": "Meghana Foods",
                "cuisine": ["Biryani", "Andhra", "Chinese"],
                "rating": 4.3,
                "delivery_time": "30-35 min",
                "cost_for_two": 500,
                "area": "Koramangala",
                "image_url": "https://example.com/meghana.jpg",
            },
            "rest_002": {
                "id": "rest_002",
                "name": "Truffles",
                "cuisine": ["American", "Burgers", "Continental"],
                "rating": 4.5,
                "delivery_time": "35-40 min",
                "cost_for_two": 700,
                "area": "Indiranagar",
                "image_url": "https://example.com/truffles.jpg",
            },
            "rest_003": {
                "id": "rest_003",
                "name": "Empire Restaurant",
                "cuisine": ["Biryani", "North Indian", "Kebabs"],
                "rating": 4.1,
                "delivery_time": "25-30 min",
                "cost_for_two": 450,
                "area": "Church Street",
                "image_url": "https://example.com/empire.jpg",
            },
            "rest_004": {
                "id": "rest_004",
                "name": "Vidyarthi Bhavan",
                "cuisine": ["South Indian", "Breakfast"],
                "rating": 4.6,
                "delivery_time": "40-45 min",
                "cost_for_two": 250,
                "area": "Basavanagudi",
                "image_url": "https://example.com/vidyarthi.jpg",
            },
            "rest_005": {
                "id": "rest_005",
                "name": "Toit Brewpub",
                "cuisine": ["Pizzas", "Continental", "Craft Beer"],
                "rating": 4.4,
                "delivery_time": "35-40 min",
                "cost_for_two": 1200,
                "area": "Indiranagar",
                "image_url": "https://example.com/toit.jpg",
            },
            "rest_006": {
                "id": "rest_006",
                "name": "MTR - Mavalli Tiffin Rooms",
                "cuisine": ["South Indian", "Desserts"],
                "rating": 4.5,
                "delivery_time": "30-35 min",
                "cost_for_two": 400,
                "area": "Lalbagh Road",
                "image_url": "https://example.com/mtr.jpg",
            },
            "rest_007": {
                "id": "rest_007",
                "name": "Nagarjuna",
                "cuisine": ["Andhra", "Biryani", "South Indian"],
                "rating": 4.2,
                "delivery_time": "25-30 min",
                "cost_for_two": 600,
                "area": "Residency Road",
                "image_url": "https://example.com/nagarjuna.jpg",
            },
            "rest_008": {
                "id": "rest_008",
                "name": "Chinita Real Mexican Food",
                "cuisine": ["Mexican", "Latin American"],
                "rating": 4.3,
                "delivery_time": "35-40 min",
                "cost_for_two": 800,
                "area": "Koramangala",
                "image_url": "https://example.com/chinita.jpg",
            },
        }

        self._menus = {
            "rest_001": [
                {"id": "item_001", "name": "Chicken Biryani", "price": 299, "is_veg": False, "description": "Andhra style dum biryani with tender chicken pieces"},
                {"id": "item_002", "name": "Mutton Biryani", "price": 399, "is_veg": False, "description": "Slow-cooked mutton dum biryani"},
                {"id": "item_003", "name": "Paneer Butter Masala", "price": 249, "is_veg": True, "description": "Creamy paneer in rich tomato gravy"},
                {"id": "item_004", "name": "Chicken 65", "price": 219, "is_veg": False, "description": "Spicy deep-fried chicken starter"},
                {"id": "item_005", "name": "Veg Fried Rice", "price": 179, "is_veg": True, "description": "Indo-Chinese style fried rice"},
            ],
            "rest_002": [
                {"id": "item_010", "name": "Classic Smash Burger", "price": 349, "is_veg": False, "description": "Double-patty smashed burger with cheese"},
                {"id": "item_011", "name": "Truffle Pasta", "price": 399, "is_veg": True, "description": "Penne in truffle cream sauce"},
                {"id": "item_012", "name": "BBQ Chicken Wings", "price": 299, "is_veg": False, "description": "Smoky BBQ glazed chicken wings"},
                {"id": "item_013", "name": "Nutella Waffle", "price": 249, "is_veg": True, "description": "Belgian waffle with Nutella and ice cream"},
            ],
            "rest_003": [
                {"id": "item_020", "name": "Empire Special Biryani", "price": 279, "is_veg": False, "description": "Signature chicken biryani"},
                {"id": "item_021", "name": "Kebab Platter", "price": 449, "is_veg": False, "description": "Assorted seekh and reshmi kebabs"},
                {"id": "item_022", "name": "Butter Naan", "price": 49, "is_veg": True, "description": "Soft butter naan"},
                {"id": "item_023", "name": "Dal Makhani", "price": 199, "is_veg": True, "description": "Slow-cooked black lentils in cream"},
            ],
            "rest_004": [
                {"id": "item_030", "name": "Masala Dosa", "price": 95, "is_veg": True, "description": "Iconic crispy dosa with potato filling"},
                {"id": "item_031", "name": "Idli Vada Combo", "price": 85, "is_veg": True, "description": "Soft idlis with crispy vada and chutney"},
                {"id": "item_032", "name": "Khara Bath", "price": 75, "is_veg": True, "description": "Spicy semolina breakfast dish"},
            ],
            "rest_005": [
                {"id": "item_040", "name": "Margherita Pizza", "price": 399, "is_veg": True, "description": "Classic mozzarella and basil"},
                {"id": "item_041", "name": "Pepperoni Pizza", "price": 499, "is_veg": False, "description": "Loaded pepperoni with mozzarella"},
                {"id": "item_042", "name": "Fish and Chips", "price": 449, "is_veg": False, "description": "Beer-battered fish with fries"},
                {"id": "item_043", "name": "Truffle Fries", "price": 299, "is_veg": True, "description": "Crispy fries with truffle oil and parmesan"},
            ],
            "rest_006": [
                {"id": "item_050", "name": "Rava Idli", "price": 80, "is_veg": True, "description": "Semolina idli with cashews and curry leaves"},
                {"id": "item_051", "name": "Filter Coffee", "price": 40, "is_veg": True, "description": "Traditional South Indian filter coffee"},
                {"id": "item_052", "name": "Badam Halwa", "price": 120, "is_veg": True, "description": "Rich almond dessert"},
            ],
            "rest_007": [
                {"id": "item_060", "name": "Andhra Meals", "price": 349, "is_veg": False, "description": "Full Andhra non-veg thali with unlimited rice"},
                {"id": "item_061", "name": "Guntur Chicken", "price": 299, "is_veg": False, "description": "Fiery Guntur-style chicken curry"},
                {"id": "item_062", "name": "Ragi Mudde", "price": 49, "is_veg": True, "description": "Finger millet balls — Karnataka staple"},
            ],
            "rest_008": [
                {"id": "item_070", "name": "Chicken Burrito Bowl", "price": 449, "is_veg": False, "description": "Grilled chicken with Mexican rice, beans, salsa"},
                {"id": "item_071", "name": "Churros", "price": 249, "is_veg": True, "description": "Cinnamon sugar churros with chocolate sauce"},
                {"id": "item_072", "name": "Loaded Nachos", "price": 349, "is_veg": True, "description": "Tortilla chips with cheese, jalapenos, guac"},
            ],
        }

        self._cart = {}

    def search_restaurants(self, query: str) -> dict:
        """Search restaurants by name or cuisine."""
        query_lower = query.lower()
        results = []
        for r in self._restaurants.values():
            name_match = query_lower in r["name"].lower()
            cuisine_match = any(query_lower in c.lower() for c in r["cuisine"])
            area_match = query_lower in r["area"].lower()
            if name_match or cuisine_match or area_match:
                results.append(r)

        # If no specific match, return all
        if not results:
            results = list(self._restaurants.values())

        return {
            "restaurants": results,
            "total": len(results),
            "query": query,
        }

    def get_restaurant_menu(self, restaurant_id: str) -> dict:
        """Get menu for a specific restaurant."""
        restaurant = self._restaurants.get(restaurant_id)
        menu = self._menus.get(restaurant_id, [])

        if not restaurant:
            return {"error": "Restaurant not found"}

        return {
            "restaurant": restaurant,
            "menu_items": menu,
            "total_items": len(menu),
        }

    def search_menu(self, query: str) -> dict:
        """Search for a dish across all restaurants."""
        query_lower = query.lower()
        results = []

        for rest_id, items in self._menus.items():
            restaurant = self._restaurants[rest_id]
            for item in items:
                if query_lower in item["name"].lower() or query_lower in item.get("description", "").lower():
                    results.append({
                        **item,
                        "restaurant_id": rest_id,
                        "restaurant_name": restaurant["name"],
                    })

        return {
            "results": results,
            "total": len(results),
            "query": query,
        }

    def update_food_cart(self, items: list) -> dict:
        """Add items to cart."""
        cart_id = str(uuid.uuid4())[:8]
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)

        self._cart[cart_id] = {
            "cart_id": cart_id,
            "items": items,
            "total": total,
            "status": "ready",
        }

        return self._cart[cart_id]

    def place_food_order(self, cart_id: str) -> dict:
        """Place an order from cart."""
        cart = self._cart.get(cart_id, {})

        return {
            "order_id": f"SWG-{uuid.uuid4().hex[:8].upper()}",
            "cart_id": cart_id,
            "status": "placed",
            "estimated_delivery": "30-35 min",
            "total": cart.get("total", 0),
            "items": cart.get("items", []),
            "placed_at": datetime.now().isoformat(),
        }
