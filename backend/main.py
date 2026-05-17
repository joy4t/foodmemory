from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import init_db
from backend.routes.health import router as health_router
from backend.routes.chat import router as chat_router
from backend.routes.ratings import router as ratings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="FoodMemory",
    description="AI food ordering copilot that remembers what you loved",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router)
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(ratings_router, prefix="/ratings", tags=["ratings"])
