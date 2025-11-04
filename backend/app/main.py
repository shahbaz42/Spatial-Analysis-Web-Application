"""Main FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import close_db
from app.routers import sites_router, analysis_router, export_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("Starting Solar Site Analyzer API...")
    print(f"Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    yield
    
    # Shutdown
    print("Shutting down Solar Site Analyzer API...")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
    #Solar Site Analyzer API
    
    API for analyzing and managing solar panel installation site suitability.
    
    # Features
    - Site Management: Query and filter potential installation sites
    - Suitability Analysis: Calculate weighted scores based on multiple factors
    - Custom Analysis: Recalculate scores with custom weight parameters
    - Statistics: Get comprehensive statistics and distributions
    - Data Export: Export filtered results in CSV or JSON format
    
    # Analysis Factors
    The suitability score (0-100) is calculated using:
    - Solar Irradiance (default weight: 0.35)
    - Available Area (default weight: 0.25)
    - Grid Distance (default weight: 0.20)
    - Terrain Slope (default weight: 0.15)
    - Infrastructure Proximity (default weight: 0.05)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sites_router, prefix=settings.API_V1_PREFIX)
app.include_router(analysis_router, prefix=settings.API_V1_PREFIX)
app.include_router(export_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "Solar Site Analyzer API",
        "version": settings.PROJECT_VERSION,
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
