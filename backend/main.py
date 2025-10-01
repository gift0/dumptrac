"""
dumpTrac FastAPI application.

This module initializes the FastAPI app, configures CORS middleware, 
sets up the database schema, and registers API routes.
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
    try:
        # Ensure tables exist (useful if Alembic migrations not run yet)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables checked/created successfully.")
    except Exception as e:
        print("❌ Error creating tables on startup:", e)
    yield
    # Optional shutdown logic

# Initialize FastAPI application
app = FastAPI(title="dumpTrac", lifespan=lifespan)

# ------------------- CORS CONFIG -------------------
ALLOWED_ORIGINS = [
    "https://dumptrac-hml5.vercel.app",  # frontend
    "https://dumptrac.vercel.app",       # backend itself
    "http://127.0.0.1:5500",             # local dev
    "http://localhost:5500",
]

# Optional: allow preview deployments from Vercel
VERCEL_URL = os.getenv("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_ORIGINS.append(f"https://{VERCEL_URL}")

# Optional: allow extra frontend URL via env
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- ROUTES -------------------
# Register API routes under /api
app.include_router(api_router, prefix="/api")

# Root health check
@app.get("/")
def root():
    return {"status": "ok", "message": "dumpTrac API is running ✅"}
