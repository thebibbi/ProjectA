# Safety Graph Twin - Graph Schema Documentation

**Version:** 1.0
**Last Updated:** 2025-11-18
**Status:** Phase 1 (M1.1)

---

## Overview

This document describes the complete graph schema for the Safety Graph Twin knowledge graph. The schema is designed to support:

- **ISO 26262** traditional safety analysis (HARA, FMEA, FTA)
- **STPA** (Systems-Theoretic Process Analysis) - Phase 5 compatible
- **Runtime monitoring** (defect tracking, discrepancy analysis)
- **Traceability** (requirements, tests, compliance)

### Design Principles

1. **Hybrid Compatibility**: Schema accommodates both traditional (FMEA/FTA) and STPA approaches
2. **Extensibility**: Optional properties and node types for future expansion
3. **Performance**: Indexes on frequently queried properties
4. **Data Integrity**: Uniqueness constraints and required properties
5. **Traceability**: Complete chains from hazards to tests

---

## Node Types

### 1. Architecture Nodes

These nodes represent the system architecture and structure.

#### 1.1 Item

Represents a high-level system or subsystem.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "ITM-001")
- `name` (string, required): Item name (e.g., "HV Battery System")
- `description` (string, optional): Detailed description
- `type` (string, optional): Item type (e.g., "system", "subsystem")

**Example:**
```cypher
CREATE (i:Item {
  id: "ITM-HV-BAT",
  name: "High Voltage Battery System",
  description: "Complete battery pack including cells, BMS, and cooling",
  type: "system"
})
```

**Typical Relationships:**
- `(Item)-[:HAS_FUNCTION]->(Function)`: Item provides functions

---

#### 1.2 Function

Represents a logical or functional block in the system.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "FN-001")
- `name` (string, required): Function name (e.g., "Torque Control")
- `description` (string, optional): Detailed description

**Example:**
```cypher
CREATE (f:Function {
  id: "FN-TORQUE-CTRL",
  name: "Torque Control",
  description: "Manages motor torque output based on driver demand"
})
```

**Typical Relationships:**
- `(Item)-[:HAS_FUNCTION]->(Function)`: Provided by item
- `(Function)-[:REALIZED_BY]->(Component)`: Implemented by components
- `(Function)-[:USES_SIGNAL]->(Signal)`: Uses signals
- `(FMEAEntry)-[:FOR_FUNCTION]->(Function)`: FMEA analysis target

---

#### 1.3 Component

Represents a concrete hardware or software element.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "C-INV-001")
- `name` (string, required): Component name
- `type` (string, required): Component type ("hardware", "software", "system")
- `version` (string, optional): Version number
- `is_critical` (boolean, optional): Safety-critical flag
- `betweenness_centrality` (float, optional): Graph metric (Phase 4)
- `pagerank` (float, optional): Graph metric (Phase 4)
- `weakness_score` (float, optional): Composite criticality score (Phase 4)

**Example:**
```cypher
CREATE (c:Component {
  id: "C-INV-GD-001",
  name: "Inverter Gate Driver",
  type: "hardware",
  version: "v2.1",
  is_critical: true
})
```

**Typical Relationships:**
- `(Function)-[:REALIZED_BY]->(Component)`: Implements function
- `(Component)-[:CONNECTED_TO]->(Component)`: Physical/logical connection
- `(Requirement)-[:ALLOCATED_TO]->(Component)`: Requirements allocation
- `(DefectInstance)-[:OBSERVED_AT]->(Component)`: Defects observed (Phase 3)

---

#### 1.4 Signal

Represents a logical or physical signal in the system.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "SIG-001")
- `name` (string, required): Signal name (e.g., "TorqueCmd")
- `unit` (string, optional): Physical unit (e.g., "Nm")
- `datatype` (string, optional): Data type (e.g., "float32", "boolean")

**Example:**
```cypher
CREATE (s:Signal {
  id: "SIG-TORQUE-CMD",
  name: "TorqueCmd",
  unit: "Nm",
  datatype: "float32"
})
```

**Typical Relationships:**
- `(Function)-[:USES_SIGNAL]->(Signal)`: Function uses signal
- `(TestCase)-[:COVERS_SIGNAL]->(Signal)`: Test coverage

---

### 2. Safety Nodes

These nodes represent safety concepts from ISO 26262 HARA and safety goals.

#### 2.1 Hazard

Represents a hazardous event or situation.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "H-001")
- `description` (string, required): Hazard description
- `asil` (string, required): ASIL rating ("A", "B", "C", "D", "QM")
- `severity` (integer, optional): Severity class (0-3 per ISO 26262)
- `exposure` (integer, optional): Exposure class (0-4 per ISO 26262)
- `controllability` (integer, optional): Controllability class (0-3 per ISO 26262)
- `coverage_status` (string, optional): Coverage status ("full", "partial", "none")

**Example:**
```cypher
CREATE (h:Hazard {
  id: "H-001",
  description: "Unintended acceleration",
  asil: "D",
  severity: 3,
  exposure: 4,
  controllability: 3,
  coverage_status: "full"
})
```

**Typical Relationships:**
- `(Hazard)-[:IN_SCENARIO]->(Scenario)`: Occurs in scenario
- `(Hazard)-[:MITIGATED_BY]->(SafetyGoal)`: Mitigated by safety goal
- `(FailureMode)-[:CAN_LEAD_TO]->(Hazard)`: Caused by failure mode
- `(DefectInstance)-[:RELATED_TO]->(Hazard)`: Related defects (Phase 3)
- `(UnsafeControlAction)-[:CAN_LEAD_TO]->(Hazard)`: STPA link (Phase 5)

---

#### 2.2 Scenario

Represents an operating scenario or operational design domain (ODD) slice.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "SC-001")
- `name` (string, required): Scenario name (e.g., "Highway driving")
- `description` (string, optional): Detailed description

**Example:**
```cypher
CREATE (sc:Scenario {
  id: "SC-HIGHWAY",
  name: "Highway driving",
  description: "Vehicle operating at >80 km/h on highway"
})
```

**Typical Relationships:**
- `(Hazard)-[:IN_SCENARIO]->(Scenario)`: Hazard occurs in scenario

---

#### 2.3 SafetyGoal

Represents a top-level safety goal from HARA.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "SG-001")
- `description` (string, required): Safety goal description
- `asil` (string, required): ASIL rating ("A", "B", "C", "D")

**Example:**
```cypher
CREATE (sg:SafetyGoal {
  id: "SG-001",
  description: "Prevent unintended acceleration >2 m/s²",
  asil: "D"
})
```

**Typical Relationships:**
- `(Hazard)-[:MITIGATED_BY]->(SafetyGoal)`: Mitigates hazard
- `(SafetyGoal)-[:REFINED_INTO]->(FunctionalSafetyRequirement)`: Refined into FSR

---

#### 2.4 FunctionalSafetyRequirement (FSR)

Represents a functional safety requirement (high-level).

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "FSR-001")
- `text` (string, required): Requirement text
- `asil` (string, required): ASIL rating ("A", "B", "C", "D")

**Example:**
```cypher
CREATE (fsr:FunctionalSafetyRequirement {
  id: "FSR-010",
  text: "Detect inverter failure within 100ms",
  asil: "D"
})
```

**Typical Relationships:**
- `(SafetyGoal)-[:REFINED_INTO]->(FunctionalSafetyRequirement)`: Derived from goal
- `(FSR)-[:REFINED_INTO]->(TechnicalSafetyRequirement)`: Further refined
- `(FSR)-[:ALLOCATED_TO]->(Item|Function|Component)`: Allocated to architecture
- `(FSR)-[:VERIFIED_BY]->(TestCase)`: Verified by tests

---

#### 2.5 TechnicalSafetyRequirement (TSR)

Represents a technical safety requirement (implementation-level).

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "TSR-001")
- `text` (string, required): Requirement text
- `asil_decomposition` (string, optional): ASIL after decomposition

**Example:**
```cypher
CREATE (tsr:TechnicalSafetyRequirement {
  id: "TSR-015",
  text: "Implement inverter watchdog timer with 50ms timeout",
  asil_decomposition: "D(D)"
})
```

**Typical Relationships:**
- `(FSR)-[:REFINED_INTO]->(TSR)`: Refined from FSR
- `(TSR)-[:ALLOCATED_TO]->(Component)`: Allocated to component
- `(TSR)-[:VERIFIED_BY]->(TestCase)`: Verified by tests

---

### 3. Analysis Nodes

These nodes represent safety analyses (FMEA, FTA).

#### 3.1 FMEAEntry

Represents an entry in a Failure Mode and Effects Analysis.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "FMEA-001")
- `failure_mode` (string, required): Failure mode description
- `effect` (string, required): Effect of failure
- `cause` (string, required): Root cause
- `detection` (string, required): Detection method
- `rpn` (integer, optional): Risk Priority Number (1-1000)
- `severity` (integer, optional): Severity rating (1-10)
- `occurrence` (integer, optional): Occurrence rating (1-10)

**Example:**
```cypher
CREATE (fmea:FMEAEntry {
  id: "FMEA-023",
  failure_mode: "Gate driver short circuit",
  effect: "Loss of torque control",
  cause: "Component wear",
  detection: "Built-in self-test",
  rpn: 240,
  severity: 8,
  occurrence: 3
})
```

**Typical Relationships:**
- `(FMEAEntry)-[:FOR_FUNCTION]->(Function)`: Analyzes function
- `(FMEAEntry)-[:HAS_FAILURE_MODE]->(FailureMode)`: Links to failure mode

---

#### 3.2 FailureMode

Represents a specific failure mode (can be shared across multiple FMEA entries).

**Properties:**
- `name` (string, required, unique): Failure mode name (e.g., "Gate driver short circuit")
- `description` (string, optional): Detailed description
- `category` (string, optional): Category (e.g., "electrical", "mechanical", "software")

**Example:**
```cypher
CREATE (fm:FailureMode {
  name: "Gate driver short circuit",
  description: "Short circuit in IGBT gate driver circuit",
  category: "electrical"
})
```

**Typical Relationships:**
- `(FMEAEntry)-[:HAS_FAILURE_MODE]->(FailureMode)`: FMEA uses this failure mode
- `(FailureMode)-[:CAN_LEAD_TO]->(Hazard)`: Can cause hazard
- `(DefectInstance)-[:INSTANCE_OF]->(FailureMode)`: Real-world instance (Phase 3)
- `(FTEvent)-[:ASSOCIATED_WITH]->(FailureMode)`: FTA reference

---

#### 3.3 FTEvent

Represents a fault tree event (basic, intermediate, or top event).

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "FT-TOP-H-001")
- `type` (string, required): Event type ("top", "intermediate", "basic")
- `description` (string, required): Event description
- `gate_type` (string, optional): Gate type ("AND", "OR", "XOR", etc.) for intermediate events

**Example:**
```cypher
CREATE (fte:FTEvent {
  id: "FT-TOP-H-001",
  type: "top",
  description: "Unintended acceleration",
  gate_type: null
})
```

**Typical Relationships:**
- `(FTEvent)-[:CAUSES]->(FTEvent)`: Causal relationship in fault tree
- `(FTEvent)-[:ASSOCIATED_WITH]->(FailureMode|Component)`: Links to architecture

---

### 4. Verification Nodes

#### 4.1 TestCase

Represents a test case for verification and validation.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "TC-001")
- `name` (string, required): Test name
- `status` (string, required): Test status ("passed", "failed", "not_run", "blocked")
- `test_type` (string, optional): Type (e.g., "unit", "integration", "HIL", "SIL")
- `coverage_level` (string, optional): Coverage level (e.g., "statement", "branch", "MC/DC")
- `description` (string, optional): Test description

**Example:**
```cypher
CREATE (tc:TestCase {
  id: "TC-045",
  name: "Inverter fault injection test",
  status: "passed",
  test_type: "HIL",
  coverage_level: "MC/DC",
  description: "Inject gate driver fault and verify detection within 100ms"
})
```

**Typical Relationships:**
- `(Requirement)-[:VERIFIED_BY]->(TestCase)`: Requirement verification
- `(TestCase)-[:COVERS_SIGNAL]->(Signal)`: Signal coverage
- `(TestCase)-[:COVERS_COMPONENT]->(Component)`: Component coverage

---

### 5. Runtime Nodes (Phase 3)

#### 5.1 DefectInstance

Represents a runtime defect or field event.

**Properties:**
- `id` (string, required, unique): Unique identifier (e.g., "D-00123")
- `timestamp` (datetime, required): When defect occurred
- `severity` (string, required): Severity ("Critical", "Major", "Minor")
- `description` (string, required): Defect description
- `status` (string, required): Status ("Open", "In Progress", "Resolved", "Closed")
- `source` (string, required): Source ("warranty", "field", "CV", "test")
- `vehicle_id` (string, optional): VIN or vehicle identifier (pseudonymized)
- `mileage` (integer, optional): Mileage when defect occurred
- `environmental_conditions` (string, optional): Environmental context

**Example:**
```cypher
CREATE (d:DefectInstance {
  id: "D-00123",
  timestamp: datetime("2025-10-15T14:30:00Z"),
  severity: "Critical",
  description: "Inverter gate driver short circuit during acceleration",
  status: "Open",
  source: "warranty",
  vehicle_id: "VIN-XXXX1234",
  mileage: 45000,
  environmental_conditions: "Temperature: 35°C, Highway"
})
```

**Typical Relationships:**
- `(DefectInstance)-[:OBSERVED_AT]->(Component)`: Component where defect observed
- `(DefectInstance)-[:INSTANCE_OF]->(FailureMode)`: Instantiates failure mode
- `(DefectInstance)-[:RELATED_TO]->(Hazard)`: Related hazard (direct or inferred)

---

### 6. STPA Nodes (Phase 5 - Placeholders)

#### 6.1 UnsafeControlAction (UCA)

Represents an unsafe control action in STPA analysis.

**Properties:**
- `id` (string, required, unique): Unique identifier
- `description` (string, required): UCA description
- `control_action` (string, required): The control action
- `context` (string, required): Context where it's unsafe
- `hazard_link` (string, optional): Link to related hazard

**Example (Phase 5):**
```cypher
CREATE (uca:UnsafeControlAction {
  id: "UCA-001",
  description: "Torque command provided when vehicle is stationary",
  control_action: "ProvideTorque",
  context: "Vehicle in park mode",
  hazard_link: "H-001"
})
```

---

#### 6.2 ControlStructure

Represents a control structure in STPA (controller, controlled process, feedback).

**Properties:**
- `id` (string, required, unique): Unique identifier
- `name` (string, required): Control structure name
- `controller_type` (string, required): Type of controller
- `controlled_process` (string, optional): What is being controlled

**Example (Phase 5):**
```cypher
CREATE (cs:ControlStructure {
  id: "CS-TORQUE-CTRL",
  name: "Torque Control Loop",
  controller_type: "software",
  controlled_process: "Motor torque output"
})
```

---

#### 6.3 LossScenario

Represents a loss scenario in STPA.

**Properties:**
- `id` (string, required, unique): Unique identifier
- `description` (string, required): Scenario description
- `causal_factors` (string, required): Causal factors leading to loss

**Example (Phase 5):**
```cypher
CREATE (ls:LossScenario {
  id: "LS-001",
  description: "Unintended torque due to sensor failure",
  causal_factors: "Position sensor drift + missing plausibility check"
})
```

---

#### 6.4 SafetyConstraint

Represents a safety constraint in STPA.

**Properties:**
- `id` (string, required, unique): Unique identifier
- `text` (string, required): Constraint text
- `relates_to_uca` (string, optional): Related UCA ID

**Example (Phase 5):**
```cypher
CREATE (sc_stpa:SafetyConstraint {
  id: "SC-STPA-001",
  text: "Torque command must not exceed driver demand by >10%",
  relates_to_uca: "UCA-001"
})
```

---

### 7. Compliance Nodes (Optional)

#### 7.1 StandardClause

Represents a clause from a safety standard (ISO 26262, ISO 21434, etc.).

**Properties:**
- `id` (string, required, unique): Unique identifier
- `standard` (string, required): Standard name (e.g., "ISO 26262:2018")
- `clause_number` (string, required): Clause number (e.g., "6.4.3")
- `title` (string, required): Clause title
- `text` (string, optional): Full clause text

**Example:**
```cypher
CREATE (clause:StandardClause {
  id: "ISO26262-6.4.3",
  standard: "ISO 26262:2018",
  clause_number: "6.4.3",
  title: "Specification of safety requirements",
  text: "..."
})
```

**Typical Relationships:**
- `(Hazard|SafetyGoal|Requirement)-[:COMPLIES_WITH]->(StandardClause)`: Compliance mapping

---

## Relationship Types

### Architecture Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `HAS_FUNCTION` | Item | Function | Item provides function |
| `REALIZED_BY` | Function | Component | Function implemented by component |
| `USES_SIGNAL` | Function | Signal | Function uses signal |
| `CONNECTED_TO` | Component | Component | Physical or logical connection |

### Safety Concept Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `IN_SCENARIO` | Hazard | Scenario | Hazard occurs in scenario |
| `MITIGATED_BY` | Hazard | SafetyGoal | Hazard mitigated by goal |
| `REFINED_INTO` | SafetyGoal | FSR | Goal refined into FSR |
| `REFINED_INTO` | FSR | TSR | FSR refined into TSR |
| `ALLOCATED_TO` | FSR/TSR | Item/Function/Component | Requirement allocation |

### Analysis Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `FOR_FUNCTION` | FMEAEntry | Function | FMEA analyzes function |
| `HAS_FAILURE_MODE` | FMEAEntry | FailureMode | FMEA includes failure mode |
| `CAN_LEAD_TO` | FailureMode | Hazard | Failure can cause hazard |
| `CAUSES` | FTEvent | FTEvent | Fault tree causality |
| `ASSOCIATED_WITH` | FTEvent | FailureMode/Component | FT event association |

### Verification Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `VERIFIED_BY` | FSR/TSR | TestCase | Requirement verified by test |
| `COVERS_SIGNAL` | TestCase | Signal | Test covers signal |
| `COVERS_COMPONENT` | TestCase | Component | Test covers component |

### Runtime Relationships (Phase 3)

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `OBSERVED_AT` | DefectInstance | Component | Defect observed at component |
| `INSTANCE_OF` | DefectInstance | FailureMode | Defect is instance of failure mode |
| `RELATED_TO` | DefectInstance | Hazard | Defect related to hazard |

### STPA Relationships (Phase 5)

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `VIOLATES` | UCA | SafetyConstraint | UCA violates constraint |
| `CAN_LEAD_TO` | UCA | Hazard | UCA can cause hazard |
| `PROVIDES` | ControlStructure | UCA | Control structure can produce UCA |
| `INVOLVES` | LossScenario | UCA | Loss scenario involves UCA |
| `ALLOCATED_TO` | SafetyConstraint | ControlStructure | Constraint allocated to control structure |

### Compliance Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `COMPLIES_WITH` | Hazard/Goal/Req | StandardClause | Compliance mapping |

---

## Indexes and Constraints

### Uniqueness Constraints

All node types have uniqueness constraints on their `id` or `name` (for FailureMode) property to prevent duplicates.

### Property Existence Constraints

Critical properties must exist:
- All nodes: `id` (except FailureMode which uses `name`)
- Hazard, SafetyGoal: `description`, `asil`
- Component, Function, Item, Signal: `name`
- TestCase: `name`, `status`
- FSR: `text`

### Performance Indexes

Indexes created for frequently queried properties:
- **ASIL-based queries**: `hazard.asil`, `safety_goal.asil`, `fsr.asil`
- **Name-based searches**: `item.name`, `component.name`, `function.name`, `signal.name`
- **Status queries**: `test_case.status`, `defect_instance.status`
- **Type filters**: `component.type`, `ft_event.type`
- **Temporal queries**: `defect_instance.timestamp`
- **Severity/RPN**: `defect_instance.severity`, `fmea_entry.rpn`

### Composite Indexes

For complex queries:
- `(hazard.asil, hazard.coverage_status)`: Coverage by ASIL
- `(test_case.status, test_case.test_type)`: Test filtering
- `(component.type, component.is_critical)`: Critical component filtering

### Full-Text Indexes

For text search:
- `hazard.description`
- `safety_goal.description`
- `fmea_entry.{failure_mode, effect, cause}`
- `test_case.{name, description}`

---

## Usage Examples

### Create Architecture

```cypher
// Create Item
CREATE (i:Item {id: "ITM-HV-BAT", name: "HV Battery System"})

// Create Function
CREATE (f:Function {id: "FN-BAT-MON", name: "Battery Monitoring"})

// Create Component
CREATE (c:Component {id: "C-BMS-001", name: "Battery Management System", type: "hardware"})

// Link them
CREATE (i)-[:HAS_FUNCTION]->(f)
CREATE (f)-[:REALIZED_BY]->(c)
```

### Create Safety Chain

```cypher
// Create Hazard
CREATE (h:Hazard {
  id: "H-015",
  description: "Battery thermal runaway",
  asil: "D",
  severity: 3,
  exposure: 2,
  controllability: 3
})

// Create Safety Goal
CREATE (sg:SafetyGoal {
  id: "SG-015",
  description: "Prevent battery temperature exceeding safe limits",
  asil: "D"
})

// Create FSR
CREATE (fsr:FunctionalSafetyRequirement {
  id: "FSR-050",
  text: "Monitor battery temperature continuously with redundancy",
  asil: "D"
})

// Create TestCase
CREATE (tc:TestCase {
  id: "TC-150",
  name: "Battery thermal monitoring test",
  status: "passed",
  test_type: "HIL"
})

// Link chain
CREATE (h)-[:MITIGATED_BY]->(sg)
CREATE (sg)-[:REFINED_INTO]->(fsr)
CREATE (fsr)-[:VERIFIED_BY]->(tc)
```

### Create FMEA Entry

```cypher
// Create FMEA Entry
CREATE (fmea:FMEAEntry {
  id: "FMEA-045",
  failure_mode: "Temperature sensor drift",
  effect: "Incorrect temperature reading",
  cause: "Sensor aging",
  detection: "Redundant sensor comparison",
  rpn: 120,
  severity: 6,
  occurrence: 4
})

// Create FailureMode (or find existing)
MERGE (fm:FailureMode {name: "Temperature sensor drift"})
SET fm.category = "hardware"

// Link FMEA to Function and FailureMode
MATCH (f:Function {id: "FN-BAT-MON"})
CREATE (fmea)-[:FOR_FUNCTION]->(f)
CREATE (fmea)-[:HAS_FAILURE_MODE]->(fm)

// Link FailureMode to Hazard
MATCH (h:Hazard {id: "H-015"})
CREATE (fm)-[:CAN_LEAD_TO]->(h)
```

---

## Migration and Versioning

### Schema Versioning

Schema version is tracked in a special node:

```cypher
MERGE (v:SchemaVersion {id: "schema_version"})
SET v.version = "1.0",
    v.last_updated = datetime(),
    v.phase = "M1.1"
```

### Adding New Node Types

When adding new node types (e.g., Phase 5 STPA nodes):

1. Add uniqueness constraint
2. Add property existence constraints
3. Add relevant indexes
4. Document relationships
5. Update schema version

### Backward Compatibility

- New properties should be optional (not required) to maintain backward compatibility
- When renaming properties, keep old property and add new one, then migrate data
- When removing node types, ensure no orphaned relationships

---

## Best Practices

### Naming Conventions

- **IDs**: Use prefixes (e.g., `H-001`, `C-INV-001`, `SG-015`)
- **Node labels**: Use PascalCase (e.g., `SafetyGoal`, not `safety_goal`)
- **Relationships**: Use UPPER_CASE (e.g., `MITIGATED_BY`, not `mitigatedBy`)
- **Properties**: Use snake_case (e.g., `coverage_status`, not `coverageStatus`)

### Data Integrity

- Always use MERGE for nodes that might already exist (e.g., FailureMode)
- Use CREATE for unique nodes (e.g., Hazard, TestCase)
- Validate ASIL values: only "A", "B", "C", "D", "QM"
- Validate status values before insertion

### Performance

- Use parameters in queries (not string concatenation)
- Leverage indexes for filtering
- Use PROFILE to analyze query performance
- Batch large imports (1000 nodes per transaction)

### Querying

- Use `MATCH` with specific labels (e.g., `MATCH (h:Hazard)` not `MATCH (h)`)
- Specify relationship directions when known
- Use `LIMIT` for exploratory queries
- Use full-text indexes for text search, not `CONTAINS`

---

## References

- **ISO 26262:2018** - Road vehicles — Functional safety
- **ISO/PAS 21448:2019** - Safety Of The Intended Functionality (SOTIF)
- **ISO/SAE 21434:2021** - Road vehicles — Cybersecurity engineering
- **STPA Handbook** - Systems-Theoretic Process Analysis
- **Neo4j Documentation** - https://neo4j.com/docs/

---

**End of Schema Documentation**
