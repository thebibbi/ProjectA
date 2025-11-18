"""
Safety Graph Twin - FastAPI Application

Main application entry point with API setup, middleware, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.neo4j_driver import close_neo4j_driver, get_neo4j_driver
from app.api import import_router, analytics_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 70)
    logger.info("Safety Graph Twin API - Starting")
    logger.info("=" * 70)

    settings = get_settings()
    logger.info(f"Environment: {'Development' if settings.is_development else 'Production'}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")
    logger.info(f"Neo4j URI: {settings.neo4j_uri}")

    # Initialize database connection
    try:
        driver = get_neo4j_driver()
        health = driver.health_check()

        if health["status"] == "healthy":
            logger.info("✓ Database connection established")

            # Log node and relationship counts
            node_counts = driver.get_node_counts()
            if node_counts:
                logger.info(f"  Node counts: {node_counts}")
            else:
                logger.info("  Database is empty (no nodes)")

        else:
            logger.warning(f"⚠ Database health check failed: {health['message']}")

    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        # Don't prevent startup - API will return 503 for database-dependent endpoints

    logger.info("=" * 70)
    logger.info("✓ Application startup complete")
    logger.info("=" * 70)

    yield

    # Shutdown
    logger.info("=" * 70)
    logger.info("Safety Graph Twin API - Shutting down")
    logger.info("=" * 70)

    # Close database connection
    close_neo4j_driver()
    logger.info("✓ Database connection closed")

    logger.info("=" * 70)
    logger.info("✓ Application shutdown complete")
    logger.info("=" * 70)


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Register API routers
app.include_router(import_router)
app.include_router(analytics_router)


# ============================================================================
# Health Check Endpoints
# ============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Basic API health check.

    Returns:
        Health status

    Example:
        ```bash
        curl http://localhost:8000/health
        ```
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "API is running",
            "version": settings.api_version,
        }
    )


@app.get("/health/db", tags=["Health"])
async def database_health_check() -> JSONResponse:
    """
    Database health check.

    Returns:
        Database health status with connection details

    Example:
        ```bash
        curl http://localhost:8000/health/db
        ```
    """
    try:
        driver = get_neo4j_driver()
        health = driver.health_check()

        status_code = 200 if health["status"] == "healthy" else 503

        return JSONResponse(
            content=health,
            status_code=status_code,
        )

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "message": "Failed to check database health",
                "details": {"error": str(e)},
            },
            status_code=503,
        )


@app.get("/health/schema", tags=["Health"])
async def schema_info() -> JSONResponse:
    """
    Get database schema information.

    Returns:
        Schema information with constraints and indexes

    Example:
        ```bash
        curl http://localhost:8000/health/schema
        ```
    """
    try:
        driver = get_neo4j_driver()
        schema = driver.get_schema_info()

        return JSONResponse(content=schema)

    except Exception as e:
        logger.error(f"Failed to get schema info: {e}")
        return JSONResponse(
            content={
                "error": str(e),
                "constraints": [],
                "indexes": [],
            },
            status_code=500,
        )


@app.get("/health/stats", tags=["Health"])
async def database_stats() -> JSONResponse:
    """
    Get database statistics.

    Returns:
        Node and relationship counts

    Example:
        ```bash
        curl http://localhost:8000/health/stats
        ```
    """
    try:
        driver = get_neo4j_driver()
        node_counts = driver.get_node_counts()
        relationship_counts = driver.get_relationship_counts()

        total_nodes = sum(node_counts.values())
        total_relationships = sum(relationship_counts.values())

        return JSONResponse(
            content={
                "nodes": {
                    "total": total_nodes,
                    "by_label": node_counts,
                },
                "relationships": {
                    "total": total_relationships,
                    "by_type": relationship_counts,
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return JSONResponse(
            content={
                "error": str(e),
                "nodes": {"total": 0, "by_label": {}},
                "relationships": {"total": 0, "by_type": {}},
            },
            status_code=500,
        )


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/", tags=["Root"])
async def root() -> JSONResponse:
    """
    API root endpoint.

    Returns:
        API information and available endpoints

    Example:
        ```bash
        curl http://localhost:8000/
        ```
    """
    return JSONResponse(
        content={
            "name": settings.api_title,
            "version": settings.api_version,
            "description": settings.api_description,
            "documentation": "/docs",
            "health_check": "/health",
            "endpoints": {
                "health": {
                    "api": "/health",
                    "database": "/health/db",
                    "schema": "/health/schema",
                    "stats": "/health/stats",
                },
                "import": {
                    "hara": "POST /import/hara",
                    "fmea": "POST /import/fmea",
                    "requirements": "POST /import/requirements",
                    "tests": "POST /import/tests",
                    "defects": "POST /import/defects",
                },
                "analytics": {
                    "hazard_coverage": "GET /analytics/coverage/hazard/{id}",
                    "all_hazards_coverage": "GET /analytics/coverage/hazards",
                    "coverage_statistics": "GET /analytics/coverage/statistics",
                    "component_impact": "GET /analytics/impact/component/{id}",
                    "all_components_impact": "GET /analytics/impact/components",
                    "traceability_chain": "GET /analytics/traceability/hazard/{id}",
                    "requirement_traceability": "GET /analytics/traceability/requirement/{id}",
                    "statistics": "GET /analytics/statistics",
                    "search_hazards": "GET /analytics/search/hazards?q={query}",
                    "search_components": "GET /analytics/search/components?q={query}",
                    "filter_hazards": "GET /analytics/filter/hazards?asil={level}",
                },
            },
        }
    )


# ============================================================================
# Exception Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.

    Args:
        request: Request object
        exc: Exception

    Returns:
        Error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        content={
            "status": "error",
            "message": "Internal server error",
            "details": str(exc) if settings.is_development else "An error occurred",
        },
        status_code=500,
    )
