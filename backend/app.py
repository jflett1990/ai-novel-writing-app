"""
Main FastAPI application entry point.

This creates the FastAPI app instance and includes all the routers.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from db.database import create_tables
from api.routes_story import router as story_router
from api.routes_character import router as character_router
from api.routes_world import router as world_router
from api.routes_generate import router as generate_router
from api.routes_export import router as export_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    print("Starting AI Novel App backend...")
    
    # Create database tables
    create_tables()
    print("Database tables created/verified")
    
    yield
    
    # Shutdown
    print("Shutting down AI Novel App backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AI-powered novel writing application backend",
    lifespan=lifespan
)

# Add CORS middleware
# Include API routers
app.include_router(story_router, prefix=f"{settings.api_v1_prefix}/stories", tags=["stories"])
app.include_router(character_router, prefix=f"{settings.api_v1_prefix}/characters", tags=["characters"])
app.include_router(world_router, prefix=f"{settings.api_v1_prefix}/world", tags=["world"])
app.include_router(generate_router, prefix=f"{settings.api_v1_prefix}/generate", tags=["generation"])
app.include_router(export_router, prefix=f"{settings.api_v1_prefix}/export", tags=["export"])

# Add CORS middleware after routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "AI Novel Writing App API",
        "version": settings.version,
        "docs_url": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
