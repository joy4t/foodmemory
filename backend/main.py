import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health_router)
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(ratings_router, prefix="/ratings", tags=["ratings"])

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the chat UI."""
    index_path = os.path.join(frontend_dir, "index.html")
    return FileResponse(index_path)
