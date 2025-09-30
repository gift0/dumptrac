from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import router as api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup logic
    Base.metadata.create_all(bind=engine)
    yield


# Initialize FastAPI application instance
app = FastAPI(title="dumpTrac", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "message": "dumpTrac API"}