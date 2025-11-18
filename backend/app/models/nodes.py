"""
Pydantic models for graph nodes.

These models represent the structure of nodes in the Neo4j graph database.
Used for validation, serialization, and type safety.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import (
    ASILLevel,
    ComponentType,
    ControllerType,
    CoverageStatus,
    DefectSeverity,
    DefectSource,
    DefectStatus,
    FailureModeCategory,
    FTEventType,
    FTGateType,
    TestStatus,
    TestType,
    CoverageLevel,
)


# ============================================================================
# ARCHITECTURE NODES
# ============================================================================


class ItemNode(BaseModel):
    """Item node in graph (high-level system/subsystem)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^(ITM|I)-[\w-]+$")
    name: str = Field(..., description="Item name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Detailed description", max_length=1000)
    type: Optional[str] = Field(None, description="Item type", max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ITM-HV-BAT",
                "name": "High Voltage Battery System",
                "description": "Complete battery pack including cells, BMS, and cooling",
                "type": "system",
            }
        }


class FunctionNode(BaseModel):
    """Function node in graph (logical/functional block)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^(FN|F)-[\w-]+$")
    name: str = Field(..., description="Function name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Detailed description", max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "FN-TORQUE-CTRL",
                "name": "Torque Control",
                "description": "Manages motor torque output based on driver demand",
            }
        }


class ComponentNode(BaseModel):
    """Component node in graph (concrete HW/SW element)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^(C|CMP)-[\w-]+$")
    name: str = Field(..., description="Component name", min_length=1, max_length=200)
    type: ComponentType = Field(..., description="Component type")
    version: Optional[str] = Field(None, description="Version", max_length=50)
    is_critical: Optional[bool] = Field(False, description="Safety-critical flag")

    # Phase 4 analytics properties
    betweenness_centrality: Optional[float] = Field(None, description="Betweenness centrality score")
    pagerank: Optional[float] = Field(None, description="PageRank score")
    weakness_score: Optional[float] = Field(None, description="Composite weakness score (0-100)", ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "C-INV-GD-001",
                "name": "Inverter Gate Driver",
                "type": "hardware",
                "version": "v2.1",
                "is_critical": True,
            }
        }


class SignalNode(BaseModel):
    """Signal node in graph (logical/physical signal)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^(SIG|S)-[\w-]+$")
    name: str = Field(..., description="Signal name", min_length=1, max_length=200)
    unit: Optional[str] = Field(None, description="Physical unit", max_length=50)
    datatype: Optional[str] = Field(None, description="Data type", max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SIG-TORQUE-CMD",
                "name": "TorqueCmd",
                "unit": "Nm",
                "datatype": "float32",
            }
        }


# ============================================================================
# SAFETY NODES
# ============================================================================


class HazardNode(BaseModel):
    """Hazard node in graph (hazardous event)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^H-[\w-]+$")
    description: str = Field(..., description="Hazard description", min_length=1, max_length=500)
    asil: ASILLevel = Field(..., description="ASIL rating")
    severity: Optional[int] = Field(None, description="Severity class (0-3)", ge=0, le=3)
    exposure: Optional[int] = Field(None, description="Exposure class (0-4)", ge=0, le=4)
    controllability: Optional[int] = Field(None, description="Controllability class (0-3)", ge=0, le=3)
    coverage_status: Optional[CoverageStatus] = Field(None, description="Test coverage status")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "H-001",
                "description": "Unintended acceleration",
                "asil": "D",
                "severity": 3,
                "exposure": 4,
                "controllability": 3,
                "coverage_status": "full",
            }
        }


class ScenarioNode(BaseModel):
    """Scenario node in graph (operating scenario/ODD)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^(SC|SCN)-[\w-]+$")
    name: str = Field(..., description="Scenario name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Detailed description", max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SC-HIGHWAY",
                "name": "Highway driving",
                "description": "Vehicle operating at >80 km/h on highway",
            }
        }


class SafetyGoalNode(BaseModel):
    """Safety Goal node in graph (from HARA)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^SG-[\w-]+$")
    description: str = Field(..., description="Safety goal description", min_length=1, max_length=500)
    asil: ASILLevel = Field(..., description="ASIL rating")

    @field_validator("asil")
    @classmethod
    def validate_safety_goal_asil(cls, v: ASILLevel) -> ASILLevel:
        """Safety goals cannot be QM."""
        if v == ASILLevel.QM:
            raise ValueError("Safety goals must have ASIL rating A, B, C, or D (not QM)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SG-001",
                "description": "Prevent unintended acceleration >2 m/s²",
                "asil": "D",
            }
        }


class FunctionalSafetyRequirementNode(BaseModel):
    """Functional Safety Requirement (FSR) node in graph."""

    id: str = Field(..., description="Unique identifier", pattern=r"^FSR-[\w-]+$")
    text: str = Field(..., description="Requirement text", min_length=1, max_length=1000)
    asil: ASILLevel = Field(..., description="ASIL rating")

    @field_validator("asil")
    @classmethod
    def validate_fsr_asil(cls, v: ASILLevel) -> ASILLevel:
        """FSR cannot be QM."""
        if v == ASILLevel.QM:
            raise ValueError("Functional Safety Requirements must have ASIL rating A, B, C, or D (not QM)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "FSR-010",
                "text": "Detect inverter failure within 100ms",
                "asil": "D",
            }
        }


class TechnicalSafetyRequirementNode(BaseModel):
    """Technical Safety Requirement (TSR) node in graph."""

    id: str = Field(..., description="Unique identifier", pattern=r"^TSR-[\w-]+$")
    text: str = Field(..., description="Requirement text", min_length=1, max_length=1000)
    asil_decomposition: Optional[str] = Field(None, description="ASIL after decomposition", max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TSR-015",
                "text": "Implement inverter watchdog timer with 50ms timeout",
                "asil_decomposition": "D(D)",
            }
        }


# ============================================================================
# ANALYSIS NODES
# ============================================================================


class FMEAEntryNode(BaseModel):
    """FMEA Entry node in graph."""

    id: str = Field(..., description="Unique identifier", pattern=r"^FMEA-[\w-]+$")
    failure_mode: str = Field(..., description="Failure mode description", min_length=1, max_length=200)
    effect: str = Field(..., description="Effect of failure", min_length=1, max_length=500)
    cause: str = Field(..., description="Root cause", min_length=1, max_length=500)
    detection: str = Field(..., description="Detection method", min_length=1, max_length=200)
    rpn: Optional[int] = Field(None, description="Risk Priority Number (1-1000)", ge=1, le=1000)
    severity: Optional[int] = Field(None, description="Severity rating (1-10)", ge=1, le=10)
    occurrence: Optional[int] = Field(None, description="Occurrence rating (1-10)", ge=1, le=10)

    @field_validator("rpn")
    @classmethod
    def validate_rpn(cls, v: Optional[int], info) -> Optional[int]:
        """Validate RPN is product of severity, occurrence, detection (if all provided)."""
        if v is not None:
            severity = info.data.get("severity")
            occurrence = info.data.get("occurrence")
            # Note: detection rating not in model yet, but RPN should be S*O*D
            # For now, just ensure it's in valid range
            if v < 1 or v > 1000:
                raise ValueError("RPN must be between 1 and 1000")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "FMEA-023",
                "failure_mode": "Gate driver short circuit",
                "effect": "Loss of torque control",
                "cause": "Component wear",
                "detection": "Built-in self-test",
                "rpn": 240,
                "severity": 8,
                "occurrence": 3,
            }
        }


class FailureModeNode(BaseModel):
    """Failure Mode node in graph (shared across FMEA entries)."""

    name: str = Field(..., description="Failure mode name (unique)", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Detailed description", max_length=1000)
    category: Optional[FailureModeCategory] = Field(None, description="Failure mode category")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Gate driver short circuit",
                "description": "Short circuit in IGBT gate driver circuit",
                "category": "electrical",
            }
        }


class FTEventNode(BaseModel):
    """Fault Tree Event node in graph."""

    id: str = Field(..., description="Unique identifier", pattern=r"^FT-[\w-]+$")
    type: FTEventType = Field(..., description="Event type")
    description: str = Field(..., description="Event description", min_length=1, max_length=500)
    gate_type: Optional[FTGateType] = Field(None, description="Gate type (for intermediate events)")

    @field_validator("gate_type")
    @classmethod
    def validate_gate_type(cls, v: Optional[FTGateType], info) -> Optional[FTGateType]:
        """Top and basic events should not have gate type."""
        event_type = info.data.get("type")
        if event_type in [FTEventType.TOP, FTEventType.BASIC] and v is not None:
            raise ValueError(f"{event_type.value} events should not have gate_type")
        if event_type == FTEventType.INTERMEDIATE and v is None:
            raise ValueError("Intermediate events must have gate_type")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "FT-TOP-H-001",
                "type": "top",
                "description": "Unintended acceleration",
                "gate_type": None,
            }
        }


# ============================================================================
# VERIFICATION NODES
# ============================================================================


class TestCaseNode(BaseModel):
    """Test Case node in graph."""

    id: str = Field(..., description="Unique identifier", pattern=r"^TC-[\w-]+$")
    name: str = Field(..., description="Test name", min_length=1, max_length=200)
    status: TestStatus = Field(..., description="Test execution status")
    test_type: Optional[TestType] = Field(None, description="Type of test")
    coverage_level: Optional[CoverageLevel] = Field(None, description="Coverage level")
    description: Optional[str] = Field(None, description="Test description", max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TC-045",
                "name": "Inverter fault injection test",
                "status": "passed",
                "test_type": "HIL",
                "coverage_level": "MC/DC",
                "description": "Inject gate driver fault and verify detection within 100ms",
            }
        }


# ============================================================================
# RUNTIME NODES (Phase 3)
# ============================================================================


class DefectInstanceNode(BaseModel):
    """Defect Instance node in graph (Phase 3)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^D-[\w-]+$")
    timestamp: datetime = Field(..., description="When defect occurred")
    severity: DefectSeverity = Field(..., description="Defect severity")
    description: str = Field(..., description="Defect description", min_length=1, max_length=1000)
    status: DefectStatus = Field(..., description="Defect status")
    source: DefectSource = Field(..., description="Source of defect report")
    vehicle_id: Optional[str] = Field(None, description="VIN or vehicle ID (pseudonymized)", max_length=100)
    mileage: Optional[int] = Field(None, description="Mileage when defect occurred", ge=0)
    environmental_conditions: Optional[str] = Field(None, description="Environmental context", max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "D-00123",
                "timestamp": "2025-10-15T14:30:00Z",
                "severity": "Critical",
                "description": "Inverter gate driver short circuit during acceleration",
                "status": "Open",
                "source": "warranty",
                "vehicle_id": "VIN-XXXX1234",
                "mileage": 45000,
                "environmental_conditions": "Temperature: 35°C, Highway",
            }
        }


# ============================================================================
# STPA NODES (Phase 5 - Placeholders)
# ============================================================================


class UnsafeControlActionNode(BaseModel):
    """Unsafe Control Action node in graph (STPA - Phase 5)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^UCA-[\w-]+$")
    description: str = Field(..., description="UCA description", min_length=1, max_length=500)
    control_action: str = Field(..., description="The control action", min_length=1, max_length=200)
    context: str = Field(..., description="Context where it's unsafe", min_length=1, max_length=500)
    hazard_link: Optional[str] = Field(None, description="Link to related hazard ID", max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "UCA-001",
                "description": "Torque command provided when vehicle is stationary",
                "control_action": "ProvideTorque",
                "context": "Vehicle in park mode",
                "hazard_link": "H-001",
            }
        }


class ControlStructureNode(BaseModel):
    """Control Structure node in graph (STPA - Phase 5)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^CS-[\w-]+$")
    name: str = Field(..., description="Control structure name", min_length=1, max_length=200)
    controller_type: ControllerType = Field(..., description="Type of controller")
    controlled_process: Optional[str] = Field(None, description="What is being controlled", max_length=200)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "CS-TORQUE-CTRL",
                "name": "Torque Control Loop",
                "controller_type": "software",
                "controlled_process": "Motor torque output",
            }
        }


class LossScenarioNode(BaseModel):
    """Loss Scenario node in graph (STPA - Phase 5)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^LS-[\w-]+$")
    description: str = Field(..., description="Scenario description", min_length=1, max_length=1000)
    causal_factors: str = Field(..., description="Causal factors leading to loss", min_length=1, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "LS-001",
                "description": "Unintended torque due to sensor failure",
                "causal_factors": "Position sensor drift + missing plausibility check",
            }
        }


class SafetyConstraintNode(BaseModel):
    """Safety Constraint node in graph (STPA - Phase 5)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^SC-STPA-[\w-]+$")
    text: str = Field(..., description="Constraint text", min_length=1, max_length=1000)
    relates_to_uca: Optional[str] = Field(None, description="Related UCA ID", max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SC-STPA-001",
                "text": "Torque command must not exceed driver demand by >10%",
                "relates_to_uca": "UCA-001",
            }
        }


# ============================================================================
# COMPLIANCE NODES (Optional)
# ============================================================================


class StandardClauseNode(BaseModel):
    """Standard Clause node in graph (ISO 26262, etc.)."""

    id: str = Field(..., description="Unique identifier", pattern=r"^[\w-]+-[\d\.]+$")
    standard: str = Field(..., description="Standard name", min_length=1, max_length=100)
    clause_number: str = Field(..., description="Clause number", min_length=1, max_length=50)
    title: str = Field(..., description="Clause title", min_length=1, max_length=200)
    text: Optional[str] = Field(None, description="Full clause text", max_length=5000)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ISO26262-6.4.3",
                "standard": "ISO 26262:2018",
                "clause_number": "6.4.3",
                "title": "Specification of safety requirements",
                "text": "...",
            }
        }
