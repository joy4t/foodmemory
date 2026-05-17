from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# --- Chat ---

class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent: Optional[str] = None
    data: Optional[dict] = None


# --- Ratings ---

class RatingCreate(BaseModel):
    user_id: str
    order_item_id: str
    restaurant_id: str
    score: int = Field(ge=1, le=5)
    note: Optional[str] = None
    would_reorder: bool = True


class RatingResponse(BaseModel):
    id: str
    item_name: str
    restaurant_name: str
    score: int
    note: Optional[str]
    would_reorder: bool
    rated_at: str


# --- Orders ---

class OrderItemOut(BaseModel):
    id: str
    item_name: str
    quantity: int
    price: float


class OrderOut(BaseModel):
    id: str
    restaurant_name: str
    order_total: float
    ordered_at: str
    status: str
    items: list[OrderItemOut] = []
