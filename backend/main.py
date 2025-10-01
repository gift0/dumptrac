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

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Startup and shutdown tasks."""
    try:
        # Create tables if not exist (useful if migrations not run)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables are ready")
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

# ----------------- Health Check -----------------
@app.get("/")
def root():
    return {"status": "ok", "message": "dumpTrac API"}
