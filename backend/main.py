"""
dumpTrac FastAPI application.

This module initializes the FastAPI app, configures CORS middleware, 
sets up the database schema, and registers API routes.

Features:
- Database tables are created on startup via SQLAlchemy.
- API routes are included under the `/api` prefix.
- A root endpoint (`/`) is provided for health/status checks.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import Base, engine
from backend.app.routes import router as api_router

# dumpTrac FastAPI backend application.


@asynccontextmanager
# Manage startup and shutdown tasks.
async def lifespan(_: FastAPI):
    # Startup logic
    Base.metadata.create_all(bind=engine)
    yield
    # (Optional) Shutdown logic

# Initialize FastAPI application instance.
app = FastAPI(title="dumpTrac", lifespan=lifespan)

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes under /api.
app.include_router(api_router, prefix="/api")


# Return API health check response.
@app.get("/")
def root():
    return {"status": "ok", "message": "dumpTrac API"}
