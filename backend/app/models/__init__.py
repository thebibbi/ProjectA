"""
Pydantic models for Safety Graph Twin.

This module provides all data models, enums, and schemas used for
validation, serialization, and type safety.
"""

# Export enums
from app.models.enums import (
    ASILLevel,
    TestStatus,
    DefectStatus,
    DefectSeverity,
    DefectSource,
    ComponentType,
    TestType,
    CoverageLevel,
    FTEventType,
    FTGateType,
    FailureModeCategory,
    CoverageStatus,
    Standard,
    ControllerType,
)

# Export node models
from app.models.nodes import (
    # Architecture nodes
    ItemNode,
    FunctionNode,
    ComponentNode,
    SignalNode,
    # Safety nodes
    HazardNode,
    ScenarioNode,
    SafetyGoalNode,
    FunctionalSafetyRequirementNode,
    TechnicalSafetyRequirementNode,
    # Analysis nodes
    FMEAEntryNode,
    FailureModeNode,
    FTEventNode,
    # Verification nodes
    TestCaseNode,
    # Runtime nodes
    DefectInstanceNode,
    # STPA nodes (Phase 5)
    UnsafeControlActionNode,
    ControlStructureNode,
    LossScenarioNode,
    SafetyConstraintNode,
    # Compliance nodes
    StandardClauseNode,
)

# Export API schemas
from app.models.schemas import (
    # Common responses
    APIResponse,
    ErrorDetail,
    ErrorResponse,
    # HARA import
    HARAImportRequest,
    HARAImportResponse,
    # FMEA import
    FMEAImportRequest,
    FMEAImportResponse,
    # Requirements import
    RequirementsImportRequest,
    RequirementsImportResponse,
    # Tests import
    TestsImportRequest,
    TestsImportResponse,
    # Defects import
    DefectsImportRequest,
    DefectsImportResponse,
    # Analytics
    TraceabilityChain,
    HazardCoverageItem,
    HazardCoverageSummary,
    HazardCoverageResponse,
    ImpactedArtifact,
    ImpactAnalysisResponse,
    StatisticsResponse,
)

__all__ = [
    # Enums
    "ASILLevel",
    "TestStatus",
    "DefectStatus",
    "DefectSeverity",
    "DefectSource",
    "ComponentType",
    "TestType",
    "CoverageLevel",
    "FTEventType",
    "FTGateType",
    "FailureModeCategory",
    "CoverageStatus",
    "Standard",
    "ControllerType",
    # Node models
    "ItemNode",
    "FunctionNode",
    "ComponentNode",
    "SignalNode",
    "HazardNode",
    "ScenarioNode",
    "SafetyGoalNode",
    "FunctionalSafetyRequirementNode",
    "TechnicalSafetyRequirementNode",
    "FMEAEntryNode",
    "FailureModeNode",
    "FTEventNode",
    "TestCaseNode",
    "DefectInstanceNode",
    "UnsafeControlActionNode",
    "ControlStructureNode",
    "LossScenarioNode",
    "SafetyConstraintNode",
    "StandardClauseNode",
    # API schemas
    "APIResponse",
    "ErrorDetail",
    "ErrorResponse",
    "HARAImportRequest",
    "HARAImportResponse",
    "FMEAImportRequest",
    "FMEAImportResponse",
    "RequirementsImportRequest",
    "RequirementsImportResponse",
    "TestsImportRequest",
    "TestsImportResponse",
    "DefectsImportRequest",
    "DefectsImportResponse",
    "TraceabilityChain",
    "HazardCoverageItem",
    "HazardCoverageSummary",
    "HazardCoverageResponse",
    "ImpactedArtifact",
    "ImpactAnalysisResponse",
    "StatisticsResponse",
]
