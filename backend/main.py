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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from app.database import Base
from app.routes import router as api_router

# Load DATABASE_URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set!")

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Run Alembic migrations on startup
def run_migrations():
    alembic_cfg = Config("migrations/alembic.ini")
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: run migrations and create tables if missing
    run_migrations()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic (optional)

# Initialize FastAPI
app = FastAPI(title="dumpTrac", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
def root():
    return {"status": "ok", "message": "dumpTrac API"}
