"""
dumpTrac FastAPI application.

Initializes FastAPI app, sets up CORS, database, and API routes.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import router as api_router

# 🔹 NEW: keepalive scheduler import (safe addition)
from app.keepalive import start_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Startup and shutdown tasks."""
    try:
        # Create tables if not exist (useful if migrations not run)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables are ready")

        # 🔹 NEW: start bi-weekly DB keepalive job
        start_scheduler()
        print("⏱️ Keepalive scheduler started")

    except Exception as e:
        print("❌ Error creating tables:", e)
    yield
    # Optional shutdown tasks


# Initialize FastAPI app
app = FastAPI(title="dumpTrac", lifespan=lifespan)

# ----------------- CORS Configuration -----------------
ALLOWED_ORIGINS = [
    "https://dumptrac-hml5.vercel.app",  # frontend
    "https://dumptrac.vercel.app",       # backend itself
    "http://127.0.0.1:5500",             # local dev
    "http://localhost:5500",
]

# Add optional preview deployment origin
VERCEL_URL = os.getenv("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_ORIGINS.append(f"https://{VERCEL_URL}")

# Add any custom frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # <- this is critical
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Routes -----------------
app.include_router(api_router, prefix="/api")

# ----------------- Debug CORS Test -----------------
@app.get("/cors-test")
def cors_test():
    """
    Quick endpoint to verify CORS is working.
    Call from frontend to check if Access-Control-Allow-Origin header is present.
    """
    return {"status": "ok", "message": "CORS is configured correctly"}

# ----------------- Health Check -----------------
@app.get("/")
def root():
    return {"status": "ok", "message": "dumpTrac API"}
