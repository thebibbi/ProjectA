# Pydantic Models

This directory contains all Pydantic models for data validation, serialization, and type safety.

## Structure

```
models/
├── __init__.py          # Exports for convenience
├── enums.py             # Enumerations (ASIL, test status, etc.)
├── nodes.py             # Graph node models
├── schemas.py           # API request/response models
└── README.md            # This file
```

## Files

### `enums.py`

Defines enumerations used throughout the application:

- **ASILLevel**: ASIL ratings (QM, A, B, C, D)
- **TestStatus**: Test execution status (passed, failed, not_run, blocked, etc.)
- **DefectStatus**: Defect status (Open, In Progress, Resolved, Closed, etc.)
- **DefectSeverity**: Defect severity (Critical, Major, Minor, Trivial)
- **DefectSource**: Source of defect (warranty, field, CV, test, internal)
- **ComponentType**: Component types (hardware, software, system, etc.)
- **TestType**: Test types (unit, integration, HIL, SIL, etc.)
- **CoverageLevel**: Coverage levels (statement, branch, MC/DC, etc.)
- **FTEventType**: Fault tree event types (top, intermediate, basic)
- **FTGateType**: Fault tree gate types (AND, OR, XOR, etc.)
- **FailureModeCategory**: Failure mode categories (electrical, mechanical, software, etc.)
- **CoverageStatus**: Hazard coverage status (full, partial, none, unknown)
- **Standard**: Safety standards (ISO 26262, ISO 21448, ISO 21434, etc.)
- **ControllerType**: STPA controller types (software, hardware, human, hybrid)

### `nodes.py`

Defines Pydantic models for graph nodes:

**Architecture Nodes:**
- `ItemNode`: System/subsystem
- `FunctionNode`: Logical/functional block
- `ComponentNode`: Concrete HW/SW element
- `SignalNode`: Logical/physical signal

**Safety Nodes:**
- `HazardNode`: Hazardous event
- `ScenarioNode`: Operating scenario
- `SafetyGoalNode`: Safety goal from HARA
- `FunctionalSafetyRequirementNode`: FSR
- `TechnicalSafetyRequirementNode`: TSR

**Analysis Nodes:**
- `FMEAEntryNode`: FMEA entry
- `FailureModeNode`: Failure mode (shared)
- `FTEventNode`: Fault tree event

**Verification Nodes:**
- `TestCaseNode`: Test case

**Runtime Nodes (Phase 3):**
- `DefectInstanceNode`: Runtime defect

**STPA Nodes (Phase 5):**
- `UnsafeControlActionNode`: UCA
- `ControlStructureNode`: Control structure
- `LossScenarioNode`: Loss scenario
- `SafetyConstraintNode`: Safety constraint

**Compliance Nodes:**
- `StandardClauseNode`: Standard clause

### `schemas.py`

Defines API request/response models:

**Common Models:**
- `APIResponse`: Base response model
- `ErrorDetail`: Error detail
- `ErrorResponse`: Error response

**Import Requests:**
- `HARAImportRequest`: HARA import
- `FMEAImportRequest`: FMEA import
- `RequirementsImportRequest`: Requirements import
- `TestsImportRequest`: Tests import
- `DefectsImportRequest`: Defects import (Phase 3)

**Import Responses:**
- `HARAImportResponse`
- `FMEAImportResponse`
- `RequirementsImportResponse`
- `TestsImportResponse`
- `DefectsImportResponse`

**Analytics Requests/Responses:**
- `TraceabilityChain`: Traceability chain model
- `HazardCoverageItem`: Hazard coverage info
- `HazardCoverageSummary`: Coverage summary
- `HazardCoverageResponse`: Coverage analysis response
- `ImpactedArtifact`: Impacted artifact
- `ImpactAnalysisResponse`: Impact analysis response
- `StatisticsResponse`: Database statistics response

## Usage

### Importing Models

```python
# Import enums
from app.models.enums import ASILLevel, TestStatus

# Import node models
from app.models.nodes import HazardNode, ComponentNode

# Import API schemas
from app.models.schemas import HARAImportRequest, HARAImportResponse
```

### Validation Example

```python
from app.models.nodes import HazardNode
from app.models.enums import ASILLevel
from pydantic import ValidationError

# Valid hazard
hazard = HazardNode(
    id="H-001",
    description="Unintended acceleration",
    asil=ASILLevel.D,
    severity=3,
    exposure=4,
    controllability=3
)

# Invalid ASIL - will raise ValidationError
try:
    invalid_hazard = HazardNode(
        id="H-001",
        description="Test",
        asil="X"  # Invalid ASIL value
    )
except ValidationError as e:
    print(e.errors())
```

### Creating API Request

```python
from app.models.schemas import HARAImportRequest
from app.models.nodes import HazardNode, SafetyGoalNode
from app.models.enums import ASILLevel

# Create import request
request = HARAImportRequest(
    hazards=[
        HazardNode(
            id="H-001",
            description="Unintended acceleration",
            asil=ASILLevel.D
        )
    ],
    safety_goals=[
        SafetyGoalNode(
            id="SG-001",
            description="Prevent unintended acceleration",
            asil=ASILLevel.D
        )
    ],
    relationships={
        "hazard_mitigated_by_goal": [["H-001", "SG-001"]]
    }
)

# Convert to dict for API
request_dict = request.model_dump()

# Convert to JSON
request_json = request.model_dump_json()
```

## Validation Rules

### ID Patterns

All IDs must follow specific patterns:

- **Item**: `ITM-*` or `I-*` (e.g., `ITM-HV-BAT`)
- **Function**: `FN-*` or `F-*` (e.g., `FN-TORQUE-CTRL`)
- **Component**: `C-*` or `CMP-*` (e.g., `C-INV-GD-001`)
- **Signal**: `SIG-*` or `S-*` (e.g., `SIG-TORQUE-CMD`)
- **Hazard**: `H-*` (e.g., `H-001`)
- **Scenario**: `SC-*` or `SCN-*` (e.g., `SC-HIGHWAY`)
- **SafetyGoal**: `SG-*` (e.g., `SG-001`)
- **FSR**: `FSR-*` (e.g., `FSR-010`)
- **TSR**: `TSR-*` (e.g., `TSR-015`)
- **FMEA**: `FMEA-*` (e.g., `FMEA-023`)
- **FTEvent**: `FT-*` (e.g., `FT-TOP-H-001`)
- **TestCase**: `TC-*` (e.g., `TC-045`)
- **Defect**: `D-*` (e.g., `D-00123`)

### ASIL Validation

- **Hazard**: Can be QM, A, B, C, or D
- **SafetyGoal**: Cannot be QM (must be A, B, C, or D)
- **FSR**: Cannot be QM (must be A, B, C, or D)
- **TSR**: Can have ASIL decomposition (e.g., "D(D)")

### RPN Validation

- **FMEAEntry**: RPN must be between 1 and 1000
- Severity and Occurrence must be between 1 and 10

### Severity Validation

- **Hazard**: Severity class 0-3 (per ISO 26262)
- **Exposure**: Exposure class 0-4 (per ISO 26262)
- **Controllability**: Controllability class 0-3 (per ISO 26262)

### Field Length Limits

- **Names**: Max 200 characters
- **Descriptions**: Max 500-1000 characters (depending on type)
- **Requirement text**: Max 1000 characters
- **IDs**: Max 50 characters

## Best Practices

### 1. Always Use Enums

Instead of:
```python
hazard = HazardNode(id="H-001", description="Test", asil="D")  # String
```

Use:
```python
from app.models.enums import ASILLevel
hazard = HazardNode(id="H-001", description="Test", asil=ASILLevel.D)  # Enum
```

### 2. Validate Early

Validate data as soon as it enters the system (at API boundary):

```python
from fastapi import HTTPException
from pydantic import ValidationError

@app.post("/import/hara")
async def import_hara(request: HARAImportRequest):
    # Validation happens automatically by FastAPI
    # If validation fails, FastAPI returns 422 with details
    pass
```

### 3. Use model_dump() for Serialization

```python
# To dict
hazard_dict = hazard.model_dump()

# To JSON
hazard_json = hazard.model_dump_json()

# Exclude None values
hazard_dict = hazard.model_dump(exclude_none=True)
```

### 4. Use model_validate() for Deserialization

```python
# From dict
hazard_data = {"id": "H-001", "description": "Test", "asil": "D"}
hazard = HazardNode.model_validate(hazard_data)

# From JSON
hazard_json = '{"id": "H-001", "description": "Test", "asil": "D"}'
hazard = HazardNode.model_validate_json(hazard_json)
```

### 5. Custom Validators

Use `@field_validator` for complex validation logic:

```python
from pydantic import field_validator

class MyModel(BaseModel):
    value: int

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v
```

## Testing Models

```python
import pytest
from pydantic import ValidationError
from app.models.nodes import HazardNode
from app.models.enums import ASILLevel

def test_valid_hazard():
    """Test creating valid hazard."""
    hazard = HazardNode(
        id="H-001",
        description="Unintended acceleration",
        asil=ASILLevel.D
    )
    assert hazard.id == "H-001"
    assert hazard.asil == ASILLevel.D

def test_invalid_hazard_id():
    """Test invalid hazard ID pattern."""
    with pytest.raises(ValidationError):
        HazardNode(
            id="INVALID-ID",  # Should start with H-
            description="Test",
            asil=ASILLevel.D
        )

def test_invalid_asil():
    """Test invalid ASIL value."""
    with pytest.raises(ValidationError):
        HazardNode(
            id="H-001",
            description="Test",
            asil="X"  # Invalid ASIL
        )

def test_safety_goal_cannot_be_qm():
    """Test that safety goals cannot be QM."""
    with pytest.raises(ValidationError):
        SafetyGoalNode(
            id="SG-001",
            description="Test",
            asil=ASILLevel.QM  # Not allowed for safety goals
        )
```

## Future Extensions

### Phase 3: Runtime Defects

- Add defect clustering models
- Add discrepancy analysis models

### Phase 4: Advanced Analytics

- Add centrality metrics to ComponentNode
- Add weak link analysis models
- Add fault tree synthesis models

### Phase 5: STPA Integration

- Populate STPA node models (currently placeholders)
- Add STPA-specific validation rules
- Add STPA analysis response models

---

**Last Updated**: 2025-11-18
**Version**: 1.0 (M1.3)
