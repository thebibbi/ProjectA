"""
Pydantic schemas for API requests and responses.

These models define the structure of data sent to and received from API endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from app.models.nodes import (
    HazardNode,
    ScenarioNode,
    SafetyGoalNode,
    FMEAEntryNode,
    FailureModeNode,
    FunctionalSafetyRequirementNode,
    TechnicalSafetyRequirementNode,
    TestCaseNode,
    DefectInstanceNode,
    ComponentNode,
)
from app.models.enums import ASILLevel, CoverageStatus


# ============================================================================
# COMMON RESPONSE MODELS
# ============================================================================


class APIResponse(BaseModel):
    """Base API response model."""

    status: str = Field(..., description="Response status: success or error")
    message: str = Field(..., description="Human-readable message")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata (timestamp, query time, etc.)")


class ErrorDetail(BaseModel):
    """Error detail model."""

    field: Optional[str] = Field(None, description="Field that caused the error")
    error: str = Field(..., description="Error message")
    value: Optional[Any] = Field(None, description="Invalid value")


class ErrorResponse(APIResponse):
    """Error response model."""

    status: str = Field(default="error", description="Always 'error'")
    errors: List[ErrorDetail] = Field(default_factory=list, description="List of errors")


# ============================================================================
# HARA IMPORT
# ============================================================================


class HARAImportRequest(BaseModel):
    """Request model for HARA import."""

    hazards: List[HazardNode] = Field(..., description="List of hazards to import")
    scenarios: List[ScenarioNode] = Field(default_factory=list, description="List of scenarios")
    safety_goals: List[SafetyGoalNode] = Field(default_factory=list, description="List of safety goals")

    relationships: Dict[str, List[List[str]]] = Field(
        default_factory=dict,
        description="Relationships between entities",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "hazards": [
                    {
                        "id": "H-001",
                        "description": "Unintended acceleration",
                        "asil": "D",
                        "severity": 3,
                        "exposure": 4,
                        "controllability": 3,
                    }
                ],
                "scenarios": [
                    {
                        "id": "SC-HIGHWAY",
                        "name": "Highway driving",
                        "description": "Vehicle operating at >80 km/h on highway",
                    }
                ],
                "safety_goals": [
                    {
                        "id": "SG-001",
                        "description": "Prevent unintended acceleration >2 m/s²",
                        "asil": "D",
                    }
                ],
                "relationships": {
                    "hazard_in_scenario": [["H-001", "SC-HIGHWAY"]],
                    "hazard_mitigated_by_goal": [["H-001", "SG-001"]],
                },
            }
        }


class HARAImportResponse(APIResponse):
    """Response model for HARA import."""

    status: str = Field(default="success", description="Import status")
    data: Dict[str, int] = Field(..., description="Import statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "HARA import completed successfully",
                "data": {
                    "hazards_created": 1,
                    "scenarios_created": 1,
                    "safety_goals_created": 1,
                    "relationships_created": 2,
                },
                "meta": {
                    "timestamp": "2025-11-18T10:30:00Z",
                    "query_time_ms": 234,
                },
            }
        }


# ============================================================================
# FMEA IMPORT
# ============================================================================


class FMEAImportRequest(BaseModel):
    """Request model for FMEA import."""

    fmea_entries: List[FMEAEntryNode] = Field(..., description="List of FMEA entries to import")
    failure_modes: List[FailureModeNode] = Field(
        default_factory=list,
        description="List of failure modes (optional, will be created if not exist)",
    )

    relationships: Dict[str, List[List[str]]] = Field(
        default_factory=dict,
        description="Relationships: for_function, has_failure_mode, can_lead_to",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "fmea_entries": [
                    {
                        "id": "FMEA-023",
                        "failure_mode": "Gate driver short circuit",
                        "effect": "Loss of torque control",
                        "cause": "Component wear",
                        "detection": "Built-in self-test",
                        "rpn": 240,
                        "severity": 8,
                        "occurrence": 3,
                    }
                ],
                "failure_modes": [
                    {
                        "name": "Gate driver short circuit",
                        "description": "Short circuit in IGBT gate driver circuit",
                        "category": "electrical",
                    }
                ],
                "relationships": {
                    "for_function": [["FMEA-023", "FN-TORQUE-CTRL"]],
                    "has_failure_mode": [["FMEA-023", "Gate driver short circuit"]],
                    "can_lead_to": [["Gate driver short circuit", "H-001"]],
                },
            }
        }


class FMEAImportResponse(APIResponse):
    """Response model for FMEA import."""

    status: str = Field(default="success", description="Import status")
    data: Dict[str, int] = Field(..., description="Import statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "FMEA import completed successfully",
                "data": {
                    "fmea_entries_created": 1,
                    "failure_modes_created": 1,
                    "failure_modes_linked": 1,
                    "relationships_created": 3,
                },
                "meta": {
                    "timestamp": "2025-11-18T10:30:00Z",
                    "query_time_ms": 156,
                },
            }
        }


# ============================================================================
# REQUIREMENTS IMPORT
# ============================================================================


class RequirementsImportRequest(BaseModel):
    """Request model for requirements import."""

    functional_safety_requirements: List[FunctionalSafetyRequirementNode] = Field(
        default_factory=list,
        description="List of FSRs",
    )
    technical_safety_requirements: List[TechnicalSafetyRequirementNode] = Field(
        default_factory=list,
        description="List of TSRs",
    )

    relationships: Dict[str, List[List[str]]] = Field(
        default_factory=dict,
        description="Relationships: refined_into, allocated_to",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "functional_safety_requirements": [
                    {
                        "id": "FSR-010",
                        "text": "Detect inverter failure within 100ms",
                        "asil": "D",
                    }
                ],
                "technical_safety_requirements": [
                    {
                        "id": "TSR-015",
                        "text": "Implement inverter watchdog timer with 50ms timeout",
                        "asil_decomposition": "D(D)",
                    }
                ],
                "relationships": {
                    "refined_into": [["SG-001", "FSR-010"], ["FSR-010", "TSR-015"]],
                    "allocated_to": [["FSR-010", "C-INV-001"], ["TSR-015", "C-INV-GD-001"]],
                },
            }
        }


class RequirementsImportResponse(APIResponse):
    """Response model for requirements import."""

    status: str = Field(default="success", description="Import status")
    data: Dict[str, int] = Field(..., description="Import statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Requirements import completed successfully",
                "data": {
                    "fsr_created": 1,
                    "tsr_created": 1,
                    "relationships_created": 4,
                },
                "meta": {
                    "timestamp": "2025-11-18T10:30:00Z",
                    "query_time_ms": 89,
                },
            }
        }


# ============================================================================
# TESTS IMPORT
# ============================================================================


class TestsImportRequest(BaseModel):
    """Request model for tests import."""

    tests: List[TestCaseNode] = Field(..., description="List of test cases to import")

    relationships: Dict[str, List[List[str]]] = Field(
        default_factory=dict,
        description="Relationships: verified_by, covers_signal, covers_component",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tests": [
                    {
                        "id": "TC-045",
                        "name": "Inverter fault injection test",
                        "status": "passed",
                        "test_type": "HIL",
                        "coverage_level": "MC/DC",
                    }
                ],
                "relationships": {
                    "verified_by": [["FSR-010", "TC-045"], ["TSR-015", "TC-045"]],
                    "covers_signal": [["TC-045", "SIG-TORQUE-CMD"]],
                    "covers_component": [["TC-045", "C-INV-GD-001"]],
                },
            }
        }


class TestsImportResponse(APIResponse):
    """Response model for tests import."""

    status: str = Field(default="success", description="Import status")
    data: Dict[str, int] = Field(..., description="Import statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Tests import completed successfully",
                "data": {
                    "tests_created": 1,
                    "relationships_created": 3,
                },
                "meta": {
                    "timestamp": "2025-11-18T10:30:00Z",
                    "query_time_ms": 67,
                },
            }
        }


# ============================================================================
# DEFECTS IMPORT (Phase 3)
# ============================================================================


class DefectsImportRequest(BaseModel):
    """Request model for defects import (Phase 3)."""

    defects: List[DefectInstanceNode] = Field(..., description="List of defect instances to import")

    relationships: Dict[str, List[List[str]]] = Field(
        default_factory=dict,
        description="Relationships: observed_at, instance_of, related_to",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "defects": [
                    {
                        "id": "D-00123",
                        "timestamp": "2025-10-15T14:30:00Z",
                        "severity": "Critical",
                        "description": "Inverter gate driver short circuit during acceleration",
                        "status": "Open",
                        "source": "warranty",
                        "vehicle_id": "VIN-XXXX1234",
                        "mileage": 45000,
                    }
                ],
                "relationships": {
                    "observed_at": [["D-00123", "C-INV-GD-001"]],
                    "instance_of": [["D-00123", "Gate driver short circuit"]],
                    "related_to": [["D-00123", "H-001"]],
                },
            }
        }


class DefectsImportResponse(APIResponse):
    """Response model for defects import (Phase 3)."""

    status: str = Field(default="success", description="Import status")
    data: Dict[str, int] = Field(..., description="Import statistics")
    warnings: List[str] = Field(default_factory=list, description="Import warnings")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Defects import completed successfully",
                "data": {
                    "defects_created": 1,
                    "components_linked": 1,
                    "failure_modes_linked": 1,
                    "hazards_inferred": 1,
                    "defects_without_component": 0,
                    "defects_without_failure_mode": 0,
                },
                "warnings": [],
                "meta": {
                    "timestamp": "2025-11-18T10:30:00Z",
                    "query_time_ms": 145,
                },
            }
        }


# ============================================================================
# HAZARD COVERAGE ANALYSIS
# ============================================================================


class TraceabilityChain(BaseModel):
    """Traceability chain from hazard to test."""

    safety_goal: str = Field(..., description="Safety goal ID")
    requirement: str = Field(..., description="Requirement ID (FSR or TSR)")
    test: str = Field(..., description="Test case ID")
    test_status: str = Field(..., description="Test execution status")


class HazardCoverageItem(BaseModel):
    """Hazard coverage information."""

    id: str = Field(..., description="Hazard ID")
    description: str = Field(..., description="Hazard description")
    asil: ASILLevel = Field(..., description="ASIL rating")
    coverage_status: CoverageStatus = Field(..., description="Coverage status")
    chains: List[TraceabilityChain] = Field(default_factory=list, description="Traceability chains")


class HazardCoverageSummary(BaseModel):
    """Summary of hazard coverage."""

    total: int = Field(..., description="Total hazards")
    full_coverage: int = Field(..., description="Hazards with full coverage")
    partial_coverage: int = Field(..., description="Hazards with partial coverage")
    no_coverage: int = Field(..., description="Hazards with no coverage")


class HazardCoverageResponse(APIResponse):
    """Response model for hazard coverage analysis."""

    status: str = Field(default="success", description="Query status")
    data: Dict[str, Any] = Field(..., description="Coverage data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "hazards": [
                        {
                            "id": "H-001",
                            "description": "Unintended acceleration",
                            "asil": "D",
                            "coverage_status": "full",
                            "chains": [
                                {
                                    "safety_goal": "SG-001",
                                    "requirement": "FSR-001",
                                    "test": "TC-001",
                                    "test_status": "passed",
                                }
                            ],
                        }
                    ],
                    "summary": {
                        "total": 15,
                        "full_coverage": 10,
                        "partial_coverage": 3,
                        "no_coverage": 2,
                    },
                },
                "meta": {
                    "timestamp": "2025-11-18T10:30:00Z",
                    "query_time_ms": 456,
                },
            }
        }


# ============================================================================
# IMPACT ANALYSIS
# ============================================================================


class ImpactedArtifact(BaseModel):
    """Impacted artifact information."""

    id: str = Field(..., description="Artifact ID")
    type: str = Field(..., description="Artifact type (Hazard, Requirement, Test, etc.)")
    description: Optional[str] = Field(None, description="Artifact description")
    asil: Optional[ASILLevel] = Field(None, description="ASIL rating (if applicable)")
    path_length: int = Field(..., description="Number of hops from component")


class ImpactAnalysisResponse(APIResponse):
    """Response model for impact analysis."""

    status: str = Field(default="success", description="Query status")
    data: Dict[str, Any] = Field(..., description="Impact analysis data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "component": {
                        "id": "C-INV-001",
                        "name": "HV Inverter Gate Driver",
                        "type": "hardware",
                    },
                    "impacted_artifacts": {
                        "hazards": [
                            {
                                "id": "H-005",
                                "type": "Hazard",
                                "description": "Loss of propulsion",
                                "asil": "C",
                                "path_length": 3,
                            }
                        ],
                        "safety_goals": [
                            {
                                "id": "SG-005",
                                "type": "SafetyGoal",
                                "description": "Maintain vehicle controllability during propulsion loss",
                                "asil": "C",
                                "path_length": 2,
                            }
                        ],
                        "requirements": [
                            {
                                "id": "FSR-010",
                                "type": "FunctionalSafetyRequirement",
                                "description": "Detect inverter failure within 100ms",
                                "asil": "D",
                                "path_length": 1,
                            }
                        ],
                        "tests": [
                            {
                                "id": "TC-045",
                                "type": "TestCase",
                                "description": "Inverter fault injection test",
                                "path_length": 2,
                            }
                        ],
                    },
                    "summary": {
                        "total_impacted": 25,
                        "critical_asil": 5,
                    },
                },
                "meta": {
                    "timestamp": "2025-11-18T10:30:00Z",
                    "query_time_ms": 567,
                },
            }
        }


# ============================================================================
# STATISTICS
# ============================================================================


class StatisticsResponse(APIResponse):
    """Response model for database statistics."""

    status: str = Field(default="success", description="Query status")
    data: Dict[str, Any] = Field(..., description="Statistics data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "nodes": {
                        "total": 523,
                        "by_label": {
                            "Hazard": 15,
                            "SafetyGoal": 15,
                            "Component": 45,
                            "TestCase": 120,
                        },
                    },
                    "relationships": {
                        "total": 876,
                        "by_type": {
                            "MITIGATED_BY": 15,
                            "VERIFIED_BY": 230,
                            "ALLOCATED_TO": 45,
                        },
                    },
                    "coverage": {
                        "hazards_with_full_coverage": 10,
                        "hazards_with_partial_coverage": 3,
                        "hazards_with_no_coverage": 2,
                        "coverage_percentage": 66.7,
                    },
                },
                "meta": {
                    "timestamp": "2025-11-18T10:30:00Z",
                    "query_time_ms": 234,
                },
            }
        }
