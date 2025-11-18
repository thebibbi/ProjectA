"""
Import API routes for Safety Graph Twin.

Provides endpoints for importing HARA, FMEA, Requirements, Tests, and Defects data.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import (
    HARAImportRequest,
    HARAImportResponse,
    FMEAImportRequest,
    FMEAImportResponse,
    RequirementsImportRequest,
    RequirementsImportResponse,
    TestsImportRequest,
    TestsImportResponse,
    DefectsImportRequest,
    DefectsImportResponse,
    ErrorResponse,
)
from app.services import (
    HARAImportService,
    FMEAImportService,
    RequirementsImportService,
    TestsImportService,
    DefectsImportService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/import",
    tags=["Import"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)


# Dependency injection for services
def get_hara_service() -> HARAImportService:
    """Get HARA import service instance."""
    return HARAImportService()


def get_fmea_service() -> FMEAImportService:
    """Get FMEA import service instance."""
    return FMEAImportService()


def get_requirements_service() -> RequirementsImportService:
    """Get Requirements import service instance."""
    return RequirementsImportService()


def get_tests_service() -> TestsImportService:
    """Get Tests import service instance."""
    return TestsImportService()


def get_defects_service() -> DefectsImportService:
    """Get Defects import service instance."""
    return DefectsImportService()


# ============================================================================
# HARA IMPORT
# ============================================================================

@router.post(
    "/hara",
    response_model=HARAImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import HARA data",
    description="""
    Import Hazard Analysis and Risk Assessment (HARA) data.

    Imports:
    - Hazards with ASIL ratings
    - Operating scenarios
    - Safety goals
    - Relationships between entities

    **Example Request:**
    ```json
    {
        "hazards": [
            {
                "id": "H-001",
                "description": "Unintended acceleration",
                "asil": "D",
                "severity": 3,
                "exposure": 4,
                "controllability": 3
            }
        ],
        "scenarios": [
            {
                "id": "SC-HIGHWAY",
                "name": "Highway driving",
                "description": "High-speed highway operation"
            }
        ],
        "safety_goals": [
            {
                "id": "SG-001",
                "description": "Prevent unintended acceleration",
                "asil": "D"
            }
        ],
        "relationships": {
            "OCCURS_IN": [["H-001", "SC-HIGHWAY"]],
            "MITIGATED_BY": [["H-001", "SG-001"]]
        }
    }
    ```

    **Example Response:**
    ```json
    {
        "status": "success",
        "message": "HARA data imported successfully",
        "data": {
            "hazards_created": 1,
            "scenarios_created": 1,
            "safety_goals_created": 1,
            "relationships_created": 2
        }
    }
    ```
    """,
)
async def import_hara(
    request: HARAImportRequest,
    service: Annotated[HARAImportService, Depends(get_hara_service)],
) -> HARAImportResponse:
    """Import HARA data into the knowledge graph."""
    try:
        logger.info("Received HARA import request")
        result = service.import_hara(request)
        logger.info(f"HARA import successful: {result.data}")
        return result

    except ValueError as e:
        logger.error(f"HARA import validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"HARA import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import HARA data: {str(e)}",
        )


# ============================================================================
# FMEA IMPORT
# ============================================================================

@router.post(
    "/fmea",
    response_model=FMEAImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import FMEA data",
    description="""
    Import Failure Mode and Effects Analysis (FMEA) data.

    Imports:
    - FMEA entries with RPN scores
    - Failure modes
    - Components (if not already present)
    - Relationships between entities

    **Example Request:**
    ```json
    {
        "components": [
            {
                "id": "C-INV-001",
                "name": "Inverter Gate Driver",
                "component_type": "hardware"
            }
        ],
        "failure_modes": [
            {
                "id": "FM-001",
                "description": "Gate driver short circuit",
                "category": "electrical"
            }
        ],
        "fmea_entries": [
            {
                "id": "FMEA-001",
                "function_description": "Control IGBT switching",
                "potential_failure": "Short circuit",
                "severity": 9,
                "occurrence": 3,
                "detection": 6,
                "rpn": 162
            }
        ],
        "relationships": {
            "HAS_FAILURE_MODE": [["C-INV-001", "FM-001"]],
            "ANALYZED_IN": [["FM-001", "FMEA-001"]]
        }
    }
    ```
    """,
)
async def import_fmea(
    request: FMEAImportRequest,
    service: Annotated[FMEAImportService, Depends(get_fmea_service)],
) -> FMEAImportResponse:
    """Import FMEA data into the knowledge graph."""
    try:
        logger.info("Received FMEA import request")
        result = service.import_fmea(request)
        logger.info(f"FMEA import successful: {result.data}")
        return result

    except ValueError as e:
        logger.error(f"FMEA import validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"FMEA import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import FMEA data: {str(e)}",
        )


# ============================================================================
# REQUIREMENTS IMPORT
# ============================================================================

@router.post(
    "/requirements",
    response_model=RequirementsImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import Requirements data",
    description="""
    Import safety requirements (FSRs and TSRs).

    Imports:
    - Functional Safety Requirements (FSRs)
    - Technical Safety Requirements (TSRs)
    - Components (if not already present)
    - Relationships: REFINED_TO, ALLOCATED_TO

    **Example Request:**
    ```json
    {
        "fsrs": [
            {
                "id": "FSR-010",
                "text": "The system shall prevent unintended acceleration",
                "asil": "D",
                "status": "approved"
            }
        ],
        "tsrs": [
            {
                "id": "TSR-015",
                "text": "Torque command shall be verified by independent channel",
                "asil": "D",
                "verification_method": "HIL testing"
            }
        ],
        "relationships": {
            "REFINED_TO": [["SG-001", "FSR-010"], ["FSR-010", "TSR-015"]],
            "ALLOCATED_TO": [["TSR-015", "C-INV-001"]]
        }
    }
    ```
    """,
)
async def import_requirements(
    request: RequirementsImportRequest,
    service: Annotated[RequirementsImportService, Depends(get_requirements_service)],
) -> RequirementsImportResponse:
    """Import requirements into the knowledge graph."""
    try:
        logger.info("Received requirements import request")
        result = service.import_requirements(request)
        logger.info(f"Requirements import successful: {result.data}")
        return result

    except ValueError as e:
        logger.error(f"Requirements import validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Requirements import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import requirements: {str(e)}",
        )


# ============================================================================
# TESTS IMPORT
# ============================================================================

@router.post(
    "/tests",
    response_model=TestsImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import Test cases",
    description="""
    Import test cases and verification relationships.

    Imports:
    - Test cases with status and coverage information
    - Relationships: VERIFIED_BY (TSR → TestCase, Component → TestCase)

    **Example Request:**
    ```json
    {
        "test_cases": [
            {
                "id": "TC-045",
                "name": "Test torque verification channel",
                "test_type": "HIL",
                "status": "passed",
                "coverage_level": "MC/DC"
            }
        ],
        "relationships": {
            "VERIFIED_BY": [["TSR-015", "TC-045"], ["C-INV-001", "TC-045"]]
        }
    }
    ```
    """,
)
async def import_tests(
    request: TestsImportRequest,
    service: Annotated[TestsImportService, Depends(get_tests_service)],
) -> TestsImportResponse:
    """Import test cases into the knowledge graph."""
    try:
        logger.info("Received tests import request")
        result = service.import_tests(request)
        logger.info(f"Tests import successful: {result.data}")
        return result

    except ValueError as e:
        logger.error(f"Tests import validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Tests import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import tests: {str(e)}",
        )


# ============================================================================
# DEFECTS IMPORT (Phase 3)
# ============================================================================

@router.post(
    "/defects",
    response_model=DefectsImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import Defects (Phase 3)",
    description="""
    Import runtime defects from warranty, field, CV, or testing.

    Imports:
    - Defect instances with severity and status
    - Relationships: FOUND_IN (Defect → Component), VIOLATES (Defect → Requirement)

    **Example Request:**
    ```json
    {
        "defects": [
            {
                "id": "D-00123",
                "title": "Gate driver overcurrent",
                "severity": "critical",
                "status": "open",
                "source": "field",
                "detected_date": "2025-11-15"
            }
        ],
        "relationships": {
            "FOUND_IN": [["D-00123", "C-INV-001"]],
            "VIOLATES": [["D-00123", "TSR-015"]]
        }
    }
    ```
    """,
)
async def import_defects(
    request: DefectsImportRequest,
    service: Annotated[DefectsImportService, Depends(get_defects_service)],
) -> DefectsImportResponse:
    """Import defects into the knowledge graph."""
    try:
        logger.info("Received defects import request")
        result = service.import_defects(request)
        logger.info(f"Defects import successful: {result.data}")
        return result

    except ValueError as e:
        logger.error(f"Defects import validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Defects import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import defects: {str(e)}",
        )
