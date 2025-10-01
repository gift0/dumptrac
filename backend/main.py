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
        # Create tables if they do not exist
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

# Allow Vercel preview deployments dynamically
VERCEL_URL = os.getenv("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_ORIGINS.append(f"https://{VERCEL_URL}")

# Allow custom frontend URLs
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # crucial for frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- API Routes -----------------
app.include_router(api_router, prefix="/api")

# ----------------- Root / Health Check -----------------
@app.get("/")
def root():
    return {"status": "ok", "message": "dumpTrac API"}
