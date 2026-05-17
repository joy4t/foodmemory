from fastapi import APIRouter
from backend.models.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main conversation endpoint. Stub — will be wired to agent orchestrator."""
    return ChatResponse(
        reply=f"FoodMemory received: '{request.message}'. Agent orchestrator coming in Phase 5.",
        intent="stub",
    )
