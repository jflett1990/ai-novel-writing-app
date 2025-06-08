"""
Main FastAPI application entry point with enhanced generation capabilities.

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
from api.routes_generate_enhanced import router as enhanced_generate_router  # New enhanced routes
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


# Creates FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AI-powered novel writing application backend with enhanced generation capabilities",
    lifespan=lifespan
)

# Include API routers
app.include_router(story_router, prefix=f"{settings.api_v1_prefix}/stories", tags=["stories"])
app.include_router(character_router, prefix=f"{settings.api_v1_prefix}/characters", tags=["characters"])
app.include_router(world_router, prefix=f"{settings.api_v1_prefix}/world", tags=["world"])

# Include both original and enhanced generation routes
app.include_router(generate_router, prefix=f"{settings.api_v1_prefix}/generate", tags=["generation"])
app.include_router(enhanced_generate_router, prefix=f"{settings.api_v1_prefix}/generate-enhanced", tags=["enhanced-generation"])

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
        "message": "AI Novel Writing App API - Enhanced Edition",
        "version": settings.version,
        "docs_url": "/docs",
        "status": "running",
        "features": {
            "enhanced_generation": True,
            "quality_controls": True,
            "multi_pass_generation": True,
            "advanced_prompting": True
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/features")
async def get_features():
    """Get information about available features."""
    return {
        "standard_generation": {
            "description": "Original generation methods",
            "endpoints": ["/api/v1/generate/*"]
        },
        "enhanced_generation": {
            "description": "Advanced generation with quality controls",
            "endpoints": ["/api/v1/generate-enhanced/*"],
            "features": [
                "Quality assessment and regeneration",
                "Multi-pass generation for highest quality",
                "Enhanced prompting with anti-generic measures",
                "Configurable target word counts (1500-5000)",
                "Chapter quality analysis",
                "Feedback-based regeneration"
            ]
        },
        "quality_controls": {
            "description": "Built-in quality assessment",
            "features": [
                "Automatic cliché detection",
                "Length validation",
                "Dialogue presence checking",
                "Repetition analysis",
                "Quality scoring (0.0-1.0)"
            ]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
