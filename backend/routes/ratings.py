from fastapi import APIRouter
from backend.models.schemas import RatingCreate
from backend.agent.memory_engine import MemoryEngine

router = APIRouter()
memory = MemoryEngine()


@router.post("/rate")
async def rate_item(rating: RatingCreate):
    """Submit a rating for an order item."""
    rating_id = await memory.record_rating(
        user_id=rating.user_id,
        order_item_id=rating.order_item_id,
        restaurant_id=rating.restaurant_id,
        score=rating.score,
        note=rating.note,
        would_reorder=rating.would_reorder,
    )
    return {"status": "saved", "rating_id": rating_id, "score": rating.score}


@router.get("/")
async def get_ratings(user_id: str, restaurant_id: str | None = None):
    """Get ratings for a user, optionally filtered by restaurant."""
    if restaurant_id:
        memory_data = await memory.get_restaurant_memory(user_id, restaurant_id)
        return {"ratings": memory_data["ratings"], "count": len(memory_data["ratings"])}
    else:
        all_ratings = await memory.get_all_user_ratings(user_id)
        return {"ratings": all_ratings, "count": len(all_ratings)}


@router.get("/context")
async def get_memory_context(user_id: str, restaurant_id: str | None = None):
    """Get the text context that would be injected into LLM prompts."""
    if restaurant_id:
        context = await memory.build_memory_context(user_id, restaurant_id)
    else:
        context = await memory.build_global_context(user_id)
    return {"context": context}
