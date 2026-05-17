from fastapi import APIRouter
from backend.models.schemas import RatingCreate

router = APIRouter()


@router.post("/rate")
async def rate_item(rating: RatingCreate):
    """Submit a rating for an order item. Stub — will be wired in Phase 8."""
    return {"status": "received", "score": rating.score}


@router.get("/")
async def get_ratings(user_id: str, restaurant_id: str | None = None):
    """Get ratings for a user. Stub — will be wired in Phase 8."""
    return {"ratings": [], "count": 0}
