"""
dumpTrac FastAPI application.

This module initializes the FastAPI app, configures CORS middleware, 
sets up the database schema, and registers API routes.

Features:
- Database tables are created on startup via SQLAlchemy.
- API routes are included under the `/api` prefix.
- A root endpoint (`/`) is provided for health/status checks.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import router as api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage startup and shutdown tasks."""
    # Startup logic
    # Commented out - tables are managed by Alembic migrations
    # Base.metadata.create_all(bind=engine)
    yield
    # (Optional) Shutdown logic


# Initialize FastAPI application instance
app = FastAPI(title="dumpTrac", lifespan=lifespan)

# Define allowed origins for CORS
ALLOWED_ORIGINS = [
    "https://dumptrac-hml5.vercel.app",  # Your frontend
    "http://127.0.0.1:5500",  # Local development
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]

# Add additional frontend URL from environment variable if set
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes under /api
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    """Return API health check response."""
    return {"status": "ok", "message": "dumpTrac API"}