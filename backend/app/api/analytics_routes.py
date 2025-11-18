"""
Analytics API routes for Safety Graph Twin.

Provides endpoints for hazard coverage, impact analysis, traceability, and statistics.
"""

import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.schemas import (
    HazardCoverageResponse,
    ImpactAnalysisResponse,
    StatisticsResponse,
    ErrorResponse,
)
from app.services import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
    },
)


# Dependency injection for service
def get_analytics_service() -> AnalyticsService:
    """Get Analytics service instance."""
    return AnalyticsService()


# ============================================================================
# HAZARD COVERAGE
# ============================================================================

@router.get(
    "/coverage/hazard/{hazard_id}",
    response_model=HazardCoverageResponse,
    summary="Get hazard coverage",
    description="""
    Get coverage analysis for a specific hazard.

    Traces the path: Hazard → SafetyGoal → FSR → TSR → TestCase

    Returns coverage status:
    - **full**: Complete traceability chain to test cases
    - **partial**: Some traceability but no test cases
    - **none**: No traceability links

    **Example Response:**
    ```json
    {
        "status": "success",
        "message": "Coverage analysis for hazard H-001",
        "data": {
            "hazard_id": "H-001",
            "coverage": {
                "hazard": {...},
                "safety_goals": [...],
                "fsrs": [...],
                "tsrs": [...],
                "test_cases": [...],
                "complete_chains": 3,
                "coverage_status": "full"
            }
        }
    }
    ```
    """,
)
async def get_hazard_coverage(
    hazard_id: str,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> HazardCoverageResponse:
    """Get coverage analysis for a specific hazard."""
    try:
        logger.info(f"Getting coverage for hazard {hazard_id}")
        result = service.get_hazard_coverage(hazard_id)
        return result

    except ValueError as e:
        logger.error(f"Hazard coverage validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get hazard coverage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hazard coverage: {str(e)}",
        )


@router.get(
    "/coverage/hazards",
    response_model=HazardCoverageResponse,
    summary="Get all hazards coverage",
    description="""
    Get coverage analysis for all hazards.

    Optional filtering by ASIL levels.

    **Query Parameters:**
    - `asil`: List of ASIL levels to filter (e.g., `?asil=C&asil=D`)

    **Example Response:**
    ```json
    {
        "status": "success",
        "message": "Coverage analysis for 50 hazard(s)",
        "data": {
            "summary": {
                "total_hazards": 50,
                "fully_covered": 35,
                "partially_covered": 10,
                "not_covered": 5,
                "coverage_percentage": 70.0
            },
            "hazards": [...]
        }
    }
    ```
    """,
)
async def get_all_hazards_coverage(
    asil: Annotated[Optional[List[str]], Query()] = None,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)] = Depends(),
) -> HazardCoverageResponse:
    """Get coverage analysis for all hazards."""
    try:
        logger.info(f"Getting coverage for all hazards (ASIL filter: {asil})")
        result = service.get_all_hazards_coverage(asil_filter=asil)
        return result

    except Exception as e:
        logger.error(f"Failed to get all hazards coverage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hazards coverage: {str(e)}",
        )


@router.get(
    "/coverage/statistics",
    summary="Get coverage statistics",
    description="""
    Get overall coverage statistics.

    Returns summary metrics:
    - Total hazards
    - Fully covered count
    - Partially covered count
    - Not covered count
    - Coverage percentage

    **Example Response:**
    ```json
    {
        "total_hazards": 50,
        "fully_covered": 35,
        "partially_covered": 10,
        "not_covered": 5,
        "coverage_percentage": 70.0
    }
    ```
    """,
)
async def get_coverage_statistics(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
):
    """Get coverage statistics."""
    try:
        logger.info("Getting coverage statistics")
        result = service.get_coverage_statistics()
        return result

    except Exception as e:
        logger.error(f"Failed to get coverage statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coverage statistics: {str(e)}",
        )


# ============================================================================
# COMPONENT IMPACT
# ============================================================================

@router.get(
    "/impact/component/{component_id}",
    response_model=ImpactAnalysisResponse,
    summary="Get component impact",
    description="""
    Get impact analysis for a specific component.

    Analyzes all artifacts connected to the component:
    - Hazards
    - Safety goals
    - Functions
    - Test cases
    - Failure modes
    - FMEA entries
    - Defects

    Calculates impact score: hazards × 10 + safety_goals × 5 + failure_modes × 3

    **Example Response:**
    ```json
    {
        "status": "success",
        "message": "Impact analysis for component C-INV-001",
        "data": {
            "component_id": "C-INV-001",
            "impact": {
                "component": {...},
                "hazards": [...],
                "safety_goals": [...],
                "functions": [...],
                "test_cases": [...],
                "failure_modes": [...],
                "fmea_entries": [...],
                "defects": [...],
                "impact_score": 87
            }
        }
    }
    ```
    """,
)
async def get_component_impact(
    component_id: str,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> ImpactAnalysisResponse:
    """Get impact analysis for a specific component."""
    try:
        logger.info(f"Getting impact for component {component_id}")
        result = service.get_component_impact(component_id)
        return result

    except ValueError as e:
        logger.error(f"Component impact validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get component impact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get component impact: {str(e)}",
        )


@router.get(
    "/impact/components",
    response_model=ImpactAnalysisResponse,
    summary="Get all components impact",
    description="""
    Get impact analysis for all components (ranked by impact score).

    **Query Parameters:**
    - `component_type`: Filter by component type (hardware, software, system)
    - `limit`: Maximum number of components to return (default: 100)

    **Example Response:**
    ```json
    {
        "status": "success",
        "message": "Impact analysis for 100 component(s)",
        "data": {
            "components": [
                {
                    "component_id": "C-INV-001",
                    "name": "Inverter Gate Driver",
                    "component_type": "hardware",
                    "hazard_count": 5,
                    "safety_goal_count": 3,
                    "failure_mode_count": 7,
                    "max_asil": "D",
                    "impact_score": 87
                },
                ...
            ],
            "total_analyzed": 100
        }
    }
    ```
    """,
)
async def get_all_components_impact(
    component_type: Annotated[Optional[str], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)] = Depends(),
) -> ImpactAnalysisResponse:
    """Get impact analysis for all components."""
    try:
        logger.info(f"Getting impact for all components (type: {component_type}, limit: {limit})")
        result = service.get_all_components_impact(
            component_type_filter=component_type,
            limit=limit
        )
        return result

    except Exception as e:
        logger.error(f"Failed to get all components impact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get components impact: {str(e)}",
        )


# ============================================================================
# TRACEABILITY
# ============================================================================

@router.get(
    "/traceability/hazard/{hazard_id}",
    summary="Get traceability chains",
    description="""
    Get complete traceability chains for a hazard.

    Returns all paths: Hazard → SafetyGoal → FSR → TSR → TestCase

    **Example Response:**
    ```json
    [
        {
            "hazard": {...},
            "safety_goal": {...},
            "fsr": {...},
            "tsr": {...},
            "test_case": {...}
        },
        ...
    ]
    ```
    """,
)
async def get_traceability_chain(
    hazard_id: str,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
):
    """Get traceability chains for a hazard."""
    try:
        logger.info(f"Getting traceability chains for hazard {hazard_id}")
        result = service.get_traceability_chain(hazard_id)
        return result

    except ValueError as e:
        logger.error(f"Traceability validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get traceability chains: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get traceability chains: {str(e)}",
        )


@router.get(
    "/traceability/requirement/{requirement_id}",
    summary="Get requirement traceability",
    description="""
    Get traceability for a requirement (upstream and downstream).

    **Example Response:**
    ```json
    {
        "requirement": {...},
        "upstream_path": [...],
        "downstream_nodes": [...]
    }
    ```
    """,
)
async def get_requirement_traceability(
    requirement_id: str,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
):
    """Get traceability for a requirement."""
    try:
        logger.info(f"Getting traceability for requirement {requirement_id}")
        result = service.get_requirement_traceability(requirement_id)
        return result

    except ValueError as e:
        logger.error(f"Requirement traceability validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get requirement traceability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get requirement traceability: {str(e)}",
        )


# ============================================================================
# STATISTICS
# ============================================================================

@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Get database statistics",
    description="""
    Get comprehensive database statistics.

    Includes:
    - Node counts by label
    - Relationship counts by type
    - ASIL distribution
    - Test status breakdown
    - Coverage percentage

    **Example Response:**
    ```json
    {
        "status": "success",
        "message": "Database statistics retrieved",
        "data": {
            "summary": {
                "total_nodes": 1234,
                "total_relationships": 2345,
                "total_hazards": 50,
                "verified_hazards": 35,
                "coverage_percentage": 70.0
            },
            "node_counts": {
                "Hazard": 50,
                "Component": 120,
                "SafetyGoal": 45,
                ...
            },
            "relationship_counts": {
                "MITIGATED_BY": 50,
                "VERIFIED_BY": 150,
                ...
            },
            "asil_distribution": {
                "Hazard": {"D": 15, "C": 20, "B": 10, "A": 5},
                ...
            },
            "test_status_counts": {
                "passed": 100,
                "failed": 5,
                "not_run": 20
            }
        }
    }
    ```
    """,
)
async def get_database_statistics(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> StatisticsResponse:
    """Get database statistics."""
    try:
        logger.info("Getting database statistics")
        result = service.get_database_statistics()
        return result

    except Exception as e:
        logger.error(f"Failed to get database statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database statistics: {str(e)}",
        )


# ============================================================================
# SEARCH AND FILTER
# ============================================================================

@router.get(
    "/search/hazards",
    summary="Search hazards",
    description="""
    Search hazards by text (ID or description).

    **Query Parameters:**
    - `q`: Search query
    - `limit`: Maximum results (default: 20)

    **Example:** `/search/hazards?q=acceleration&limit=10`
    """,
)
async def search_hazards(
    q: Annotated[str, Query(min_length=1)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)] = Depends(),
):
    """Search hazards by text."""
    try:
        logger.info(f"Searching hazards for: {q}")
        result = service.search_hazards(q, limit)
        return {"results": result, "count": len(result)}

    except Exception as e:
        logger.error(f"Failed to search hazards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search hazards: {str(e)}",
        )


@router.get(
    "/search/components",
    summary="Search components",
    description="""
    Search components by text (ID, name, or description).

    **Query Parameters:**
    - `q`: Search query
    - `limit`: Maximum results (default: 20)

    **Example:** `/search/components?q=inverter&limit=10`
    """,
)
async def search_components(
    q: Annotated[str, Query(min_length=1)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)] = Depends(),
):
    """Search components by text."""
    try:
        logger.info(f"Searching components for: {q}")
        result = service.search_components(q, limit)
        return {"results": result, "count": len(result)}

    except Exception as e:
        logger.error(f"Failed to search components: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search components: {str(e)}",
        )


@router.get(
    "/filter/hazards",
    summary="Filter hazards by ASIL",
    description="""
    Filter hazards by ASIL levels.

    **Query Parameters:**
    - `asil`: List of ASIL levels (e.g., `?asil=C&asil=D`)

    **Example:** `/filter/hazards?asil=C&asil=D`
    """,
)
async def filter_hazards_by_asil(
    asil: Annotated[List[str], Query()],
    service: Annotated[AnalyticsService, Depends(get_analytics_service)] = Depends(),
):
    """Filter hazards by ASIL levels."""
    try:
        logger.info(f"Filtering hazards by ASIL: {asil}")
        result = service.filter_hazards_by_asil(asil)
        return {"results": result, "count": len(result)}

    except Exception as e:
        logger.error(f"Failed to filter hazards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to filter hazards: {str(e)}",
        )
