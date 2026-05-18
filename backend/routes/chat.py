from fastapi import APIRouter
from backend.models.schemas import ChatRequest, ChatResponse
from backend.agent.orchestrator import AgentOrchestrator

router = APIRouter()
agent = AgentOrchestrator()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main conversation endpoint — routes through agent orchestrator."""
    result = await agent.process(request.user_id, request.message)
    return ChatResponse(
        reply=result["reply"],
        intent=result.get("intent"),
        data=result.get("data"),
    )
