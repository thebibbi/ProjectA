# Product Requirements Document: Phase 1 - Core Knowledge Graph & ETL

**Project:** Safety Graph Twin
**Phase:** M1 - Core KG & ETL
**Version:** 1.0
**Date:** 2025-11-18
**Status:** Planning

---

## 1. Executive Summary

### 1.1 Overview

Phase 1 establishes the foundational knowledge graph infrastructure for the Safety Graph Twin system. This phase delivers a fully functional backend API capable of importing ISO 26262 safety artifacts (HARA, FMEA, requirements, tests) into a Neo4j graph database and performing critical safety analytics queries.

### 1.2 Business Objectives

- **Unify Safety Artifacts:** Break down silos between HARA, FMEA, requirements, and test documentation
- **Enable Impact Analysis:** Answer "what breaks if X changes?" within seconds instead of days
- **Improve Coverage Visibility:** Identify untested hazards and gaps in safety chains immediately
- **Establish Foundation:** Create extensible platform for future runtime monitoring (Phase 3)

### 1.3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Import Speed | <10 seconds for 1000 nodes | Benchmark with seed data |
| Query Response Time | <1 second for coverage analysis | P95 latency |
| Coverage Analysis Accuracy | 100% correct gap detection | Manual verification vs expected results |
| API Availability | >99% uptime | Health check monitoring |
| Documentation Completeness | Non-expert can run demo in <30 minutes | User testing |

---

## 2. Problem Statement

### 2.1 Current Pain Points

**For Safety Engineers:**
- Safety artifacts scattered across Excel, Confluence, DOORS, and tool-specific formats
- Impact analysis requires manual trace through multiple documents (days of work)
- No automated coverage analysis - gaps discovered late in V&V phase
- Change management triggers expensive full re-analysis

**For Systems Engineers:**
- Component changes have unknown safety implications until formal review
- Requirements traceability is manual and error-prone
- No visibility into which components are "safety critical hubs"

**For Compliance Teams:**
- Auditing traceability for ISO 26262 requires assembling evidence from multiple sources
- Demonstrating "no single point of failure" requires manual analysis

### 2.2 Target Users

**Primary:**
- Functional Safety Engineers (ISO 26262 experts)
- Systems Engineers (architecture and requirements owners)

**Secondary:**
- Test Engineers (need traceability to requirements)
- Project Managers (need coverage dashboards)
- Auditors (need evidence of compliance)

---

## 3. Requirements

### 3.1 Functional Requirements

#### FR1: Graph Database Schema

**FR1.1 Node Types**
- MUST support 12+ node types: Item, Function, Component, Signal, Hazard, Scenario, SafetyGoal, FunctionalSafetyRequirement, TechnicalSafetyRequirement, TestCase, FMEAEntry, FailureMode, FTEvent
- MUST enforce uniqueness on ID property for all node types
- MUST support ASIL property (A, B, C, D, QM) with validation
- SHOULD support optional properties for extensibility

**FR1.2 Relationship Types**
- MUST support architecture relationships: HAS_FUNCTION, REALIZED_BY, USES_SIGNAL, CONNECTED_TO
- MUST support safety relationships: IN_SCENARIO, MITIGATED_BY, REFINED_INTO, ALLOCATED_TO, VERIFIED_BY
- MUST support analysis relationships: FOR_FUNCTION, HAS_FAILURE_MODE, CAN_LEAD_TO, CAUSES, ASSOCIATED_WITH
- SHOULD support properties on relationships (e.g., allocation rationale)

**FR1.3 Constraints & Indexes**
- MUST create uniqueness constraints on (NodeType, id) pairs
- MUST create indexes on: name, asil, status properties
- SHOULD create composite indexes for common query patterns

#### FR2: Data Import

**FR2.1 HARA Import**
- MUST accept JSON payload with hazards, scenarios, safety goals
- MUST validate ASIL values (A, B, C, D, QM)
- MUST create bidirectional relationships (Hazard MITIGATED_BY SafetyGoal)
- MUST handle duplicate IDs gracefully (update or reject with clear error)
- SHOULD support CSV file upload with automatic parsing
- SHOULD provide import summary (X nodes created, Y relationships, Z errors)

**FR2.2 FMEA Import**
- MUST accept FMEA entries with failure modes, causes, effects, RPN
- MUST validate RPN range (1-1000)
- MUST create/reuse FailureMode nodes (avoid duplicates)
- MUST link FailureMode CAN_LEAD_TO Hazard
- MUST link FMEAEntry FOR_FUNCTION Function
- SHOULD support severity/occurrence/detection components separately

**FR2.3 Requirements Import**
- MUST accept FSR and TSR with unique IDs
- MUST support ALLOCATED_TO relationships to Item/Function/Component
- MUST link SafetyGoal REFINED_INTO FunctionalSafetyRequirement
- SHOULD support ASIL decomposition for TSR

**FR2.4 Test Import**
- MUST accept test cases with status (passed, failed, not_run, blocked)
- MUST link (Requirement VERIFIED_BY TestCase)
- SHOULD support test coverage level metadata
- SHOULD link (TestCase COVERS_SIGNAL Signal)

**FR2.5 Batch Import**
- MUST support transaction rollback on import errors
- MUST process imports in batches for large datasets (>1000 nodes)
- SHOULD provide progress indication for long-running imports
- SHOULD validate data before database insertion

#### FR3: Analytics Queries

**FR3.1 Hazard Coverage Analysis**
- MUST identify hazards with NO path to TestCase
- MUST identify hazards with PARTIAL coverage (some goals/requirements untested)
- MUST identify hazards with FULL coverage (all paths reach tests with status=passed)
- MUST return the full traceability chain for each hazard
- SHOULD support filtering by ASIL level

**FR3.2 Impact Analysis**
- MUST accept component ID as input
- MUST traverse graph up to 4 hops from component
- MUST return all affected: Hazards, SafetyGoals, Requirements, TestCases, FMEAEntries, FTEvents
- MUST return the path from component to each affected artifact
- SHOULD rank affected artifacts by safety criticality

**FR3.3 Gap Analysis**
- MUST identify requirements without verification (no VERIFIED_BY link)
- MUST identify safety goals without requirements (no REFINED_INTO link)
- MUST identify failure modes without hazard linkage
- SHOULD provide recommendation for closing gaps

**FR3.4 Statistics**
- MUST return counts: total hazards, total requirements, total tests, total components
- MUST return coverage percentage (hazards with full coverage / total hazards)
- MUST return ASIL distribution (count per ASIL level)
- SHOULD return import history (last import time, record counts)

#### FR4: API Endpoints

**FR4.1 Import Endpoints**
- `POST /import/hara` - Import HARA data (JSON or multipart CSV)
- `POST /import/fmea` - Import FMEA data
- `POST /import/requirements` - Import requirements
- `POST /import/tests` - Import test cases
- ALL import endpoints MUST return:
  - HTTP 200 on success with summary
  - HTTP 400 on validation error with detailed error messages
  - HTTP 500 on database error with error ID for troubleshooting

**FR4.2 Analytics Endpoints**
- `GET /analytics/hazard-coverage` - Get coverage for all hazards
  - Query params: `asil` (filter), `status` (filter), `limit`, `offset`
- `GET /analytics/impact/component/{component_id}` - Get impact analysis
  - Path param: component_id
  - Query param: `max_hops` (default 4)
- `GET /analytics/gaps` - Get gap analysis
- `GET /analytics/statistics` - Get overview statistics

**FR4.3 Health Endpoints**
- `GET /health` - API health check (MUST return 200 if API running)
- `GET /health/db` - Database health check (MUST test Neo4j connection)

**FR4.4 API Documentation**
- MUST provide OpenAPI/Swagger documentation at `/docs`
- MUST include example requests and responses
- SHOULD include cURL examples for all endpoints

### 3.2 Non-Functional Requirements

#### NFR1: Performance

- Import operations MUST complete within 10 seconds for 1000 nodes
- Analytics queries MUST return within 1 second for graphs <10K nodes
- API MUST support 100 concurrent requests
- Database queries MUST use indexes (validated with EXPLAIN)

#### NFR2: Reliability

- Import operations MUST be transactional (atomic commit or rollback)
- Database connection MUST auto-reconnect on failure
- API MUST log all errors with unique request ID
- System MUST handle Neo4j downtime gracefully (return 503 Service Unavailable)

#### NFR3: Security

- API MUST validate all inputs (Pydantic schemas)
- Cypher queries MUST use parameterization (prevent injection)
- Sensitive errors MUST NOT expose internal details to clients
- SHOULD implement rate limiting (100 requests/minute per IP)

#### NFR4: Maintainability

- Code MUST have type hints (Python) for all functions
- Code MUST pass linting (Ruff) and formatting (Black)
- Code MUST have docstrings for all public functions
- MUST achieve >80% test coverage on core logic
- Cypher queries MUST be in separate module (not inline in endpoints)

#### NFR5: Observability

- All requests MUST be logged with: timestamp, method, path, status, duration
- Database operations MUST be logged with query time
- Import operations MUST log summary statistics
- Errors MUST be logged with full stack trace

#### NFR6: Deployment

- Backend MUST run in Docker container
- MUST provide docker-compose.yml for full stack (Neo4j + backend)
- MUST support configuration via environment variables
- MUST include health check in Docker container

---

## 4. Technical Architecture

### 4.1 System Components

```
┌─────────────────┐
│   API Client    │  (Postman, cURL, frontend)
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   FastAPI App   │  (Python 3.11+)
│                 │
│  ┌───────────┐  │
│  │ Endpoints │  │  (import, analytics, health)
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │ Services  │  │  (business logic)
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  Queries  │  │  (Cypher queries)
│  └─────┬─────┘  │
└────────┼────────┘
         │ Neo4j Driver
         ▼
┌─────────────────┐
│    Neo4j DB     │  (Graph database)
│                 │
│  Nodes:         │
│  - Item         │
│  - Function     │
│  - Component    │
│  - Hazard       │
│  - SafetyGoal   │
│  - ...          │
└─────────────────┘
```

### 4.2 Technology Stack

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Graph DB | Neo4j Community | 5.15+ | Mature ecosystem, excellent Cypher support, free for development |
| Backend Framework | FastAPI | 0.115+ | High performance, async support, native Pydantic integration |
| Language | Python | 3.11+ | Rich ecosystem, excellent Neo4j driver, type hints |
| Validation | Pydantic | 2.5+ | Type-safe, 2.5x faster than alternatives, FastAPI native |
| Dependency Mgmt | Poetry | 1.8+ | Reproducible builds, better than pip+requirements.txt |
| Database Driver | neo4j (official) | 5.15+ | Official support, connection pooling, async support |
| Testing | pytest | 8.0+ | Industry standard, excellent async support |
| Containerization | Docker | 24+ | Consistent deployment, easy local development |

### 4.3 Data Flow

**Import Flow:**
```
CSV/JSON File
  ↓
FastAPI Endpoint (POST /import/*)
  ↓
Pydantic Validation
  ↓
Service Layer (business logic)
  ↓
Cypher Query Execution
  ↓
Neo4j Database (transactional write)
  ↓
Response (success/error + summary)
```

**Query Flow:**
```
HTTP Request (GET /analytics/*)
  ↓
FastAPI Endpoint
  ↓
Service Layer
  ↓
Cypher Query with Parameters
  ↓
Neo4j Database (read)
  ↓
Result Processing (format for API)
  ↓
JSON Response
```

### 4.4 Database Schema (Simplified)

**Core Nodes:**
```cypher
// Architecture
(:Item {id, name, description, type})
(:Function {id, name, description})
(:Component {id, name, type, version})
(:Signal {id, name, unit, datatype})

// Safety
(:Hazard {id, description, asil, severity, exposure, controllability})
(:Scenario {id, name, description})
(:SafetyGoal {id, description, asil})
(:FunctionalSafetyRequirement {id, text, asil})
(:TechnicalSafetyRequirement {id, text, asil_decomposition})

// Analysis
(:FMEAEntry {id, failure_mode, effect, cause, detection, rpn, severity, occurrence})
(:FailureMode {name, description, category})
(:FTEvent {id, type, description, gate_type})

// Verification
(:TestCase {id, name, status, test_type, coverage_level})
```

**Key Relationships:**
```cypher
(Hazard)-[:MITIGATED_BY]->(SafetyGoal)
(SafetyGoal)-[:REFINED_INTO]->(FunctionalSafetyRequirement)
(FunctionalSafetyRequirement)-[:ALLOCATED_TO]->(Component)
(FunctionalSafetyRequirement)-[:VERIFIED_BY]->(TestCase)
(FMEAEntry)-[:HAS_FAILURE_MODE]->(FailureMode)
(FailureMode)-[:CAN_LEAD_TO]->(Hazard)
```

---

## 5. API Specification

### 5.1 Import HARA

**Endpoint:** `POST /import/hara`

**Request Body:**
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
      "id": "SC-001",
      "name": "Highway driving",
      "description": "Vehicle operating at >80 km/h on highway"
    }
  ],
  "safety_goals": [
    {
      "id": "SG-001",
      "description": "Prevent unintended acceleration >2 m/s²",
      "asil": "D"
    }
  ],
  "relationships": {
    "hazard_in_scenario": [["H-001", "SC-001"]],
    "hazard_mitigated_by_goal": [["H-001", "SG-001"]]
  }
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "hazards_created": 1,
    "scenarios_created": 1,
    "safety_goals_created": 1,
    "relationships_created": 2
  },
  "message": "HARA import completed successfully",
  "meta": {
    "timestamp": "2025-11-18T10:30:00Z",
    "query_time_ms": 234
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Validation error",
  "errors": [
    {
      "field": "hazards[0].asil",
      "error": "Invalid ASIL value 'X'. Must be one of: A, B, C, D, QM"
    }
  ],
  "meta": {
    "timestamp": "2025-11-18T10:30:00Z"
  }
}
```

### 5.2 Hazard Coverage Analysis

**Endpoint:** `GET /analytics/hazard-coverage?asil=D&limit=50`

**Response:**
```json
{
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
            "test_status": "passed"
          }
        ]
      },
      {
        "id": "H-002",
        "description": "Loss of braking",
        "asil": "D",
        "coverage_status": "none",
        "chains": []
      }
    ],
    "summary": {
      "total": 15,
      "full_coverage": 10,
      "partial_coverage": 3,
      "no_coverage": 2
    }
  },
  "meta": {
    "timestamp": "2025-11-18T10:30:00Z",
    "query_time_ms": 456
  }
}
```

### 5.3 Impact Analysis

**Endpoint:** `GET /analytics/impact/component/C-INV-001?max_hops=4`

**Response:**
```json
{
  "status": "success",
  "data": {
    "component": {
      "id": "C-INV-001",
      "name": "HV Inverter Gate Driver",
      "type": "hardware"
    },
    "impacted_artifacts": {
      "hazards": [
        {
          "id": "H-005",
          "description": "Loss of propulsion",
          "asil": "C",
          "path_length": 3
        }
      ],
      "safety_goals": [
        {
          "id": "SG-005",
          "description": "Maintain vehicle controllability during propulsion loss",
          "asil": "C",
          "path_length": 2
        }
      ],
      "requirements": [
        {
          "id": "FSR-010",
          "text": "Detect inverter failure within 100ms",
          "asil": "C",
          "path_length": 1
        }
      ],
      "tests": [
        {
          "id": "TC-045",
          "name": "Inverter fault injection test",
          "status": "passed",
          "path_length": 2
        }
      ],
      "fmea_entries": [
        {
          "id": "FMEA-023",
          "failure_mode": "Gate driver short circuit",
          "rpn": 240,
          "path_length": 1
        }
      ]
    },
    "summary": {
      "total_impacted": 25,
      "critical_asil": 5
    }
  },
  "meta": {
    "timestamp": "2025-11-18T10:30:00Z",
    "query_time_ms": 567
  }
}
```

---

## 6. Data Model

### 6.1 Node Properties

**Hazard:**
| Property | Type | Required | Description | Validation |
|----------|------|----------|-------------|------------|
| id | string | Yes | Unique identifier | Pattern: H-\d+ |
| description | string | Yes | Hazard description | Max 500 chars |
| asil | string | Yes | ASIL rating | One of: A, B, C, D, QM |
| severity | integer | No | Severity class | 0-3 |
| exposure | integer | No | Exposure class | 0-4 |
| controllability | integer | No | Controllability class | 0-3 |

**SafetyGoal:**
| Property | Type | Required | Description | Validation |
|----------|------|----------|-------------|------------|
| id | string | Yes | Unique identifier | Pattern: SG-\d+ |
| description | string | Yes | Goal description | Max 500 chars |
| asil | string | Yes | ASIL rating | One of: A, B, C, D |

**FunctionalSafetyRequirement:**
| Property | Type | Required | Description | Validation |
|----------|------|----------|-------------|------------|
| id | string | Yes | Unique identifier | Pattern: FSR-\d+ |
| text | string | Yes | Requirement text | Max 1000 chars |
| asil | string | Yes | ASIL rating | One of: A, B, C, D |

**TestCase:**
| Property | Type | Required | Description | Validation |
|----------|------|----------|-------------|------------|
| id | string | Yes | Unique identifier | Pattern: TC-\d+ |
| name | string | Yes | Test name | Max 200 chars |
| status | string | Yes | Test status | One of: passed, failed, not_run, blocked |
| test_type | string | No | Type of test | E.g., unit, integration, HIL |
| coverage_level | string | No | Coverage level | E.g., statement, branch, MC/DC |

**Component:**
| Property | Type | Required | Description | Validation |
|----------|------|----------|-------------|------------|
| id | string | Yes | Unique identifier | Pattern: C-[A-Z]+-\d+ |
| name | string | Yes | Component name | Max 200 chars |
| type | string | Yes | Component type | E.g., hardware, software, system |
| version | string | No | Version | Semver format |

**FMEAEntry:**
| Property | Type | Required | Description | Validation |
|----------|------|----------|-------------|------------|
| id | string | Yes | Unique identifier | Pattern: FMEA-\d+ |
| failure_mode | string | Yes | Failure mode | Max 200 chars |
| effect | string | Yes | Effect of failure | Max 500 chars |
| cause | string | Yes | Root cause | Max 500 chars |
| detection | string | Yes | Detection method | Max 200 chars |
| rpn | integer | No | Risk Priority Number | 1-1000 |
| severity | integer | No | Severity rating | 1-10 |
| occurrence | integer | No | Occurrence rating | 1-10 |

### 6.2 Relationship Properties

Most relationships are simple (no properties), but some may have optional metadata:

**ALLOCATED_TO:**
- `rationale` (string): Reason for allocation
- `allocation_date` (string): ISO 8601 timestamp

**VERIFIED_BY:**
- `verification_method` (string): E.g., test, analysis, inspection, review
- `verification_date` (string): ISO 8601 timestamp

---

## 7. Seed Data

### 7.1 Example Scenario: Electric Vehicle Inverter System

**Scope:**
- 3 Items (HV Battery, Inverter, Motor)
- 5 Functions (TorqueControl, InverterDrive, MotorControl, BatteryMonitoring, SafetyMonitoring)
- 8 Components (BMS, InverterController, GateDriver, IGBT, Motor, Resolver, SafetyMCU, CAN)
- 10 Signals (TorqueCmd, Current, Voltage, Temperature, Position, Speed, FaultStatus, etc.)
- 5 Hazards (UnintendedAcceleration, LossOfBraking, LossOfPropulsion, ElectricalShock, ThermalRunaway)
- 5 Scenarios (Highway, Urban, Parking, Charging, Emergency)
- 5 Safety Goals (one per hazard)
- 10 FSR (2 per safety goal)
- 15 TSR (refinements of FSR)
- 12 FMEA Entries (covering key failure modes)
- 8 Failure Modes (InverterShort, GateDriverFailure, SensorDrift, etc.)
- 20 Test Cases (unit, integration, HIL)

**Coverage:**
- 3 hazards with full coverage (hazard → goal → FSR → TSR → test with passed status)
- 1 hazard with partial coverage (missing test for one TSR)
- 1 hazard with no coverage (safety goal exists but no requirements)

### 7.2 CSV Format Examples

**hara_example.csv:**
```csv
hazard_id,hazard_description,asil,severity,exposure,controllability,scenario_id,scenario_name,safety_goal_id,safety_goal_description,safety_goal_asil
H-001,Unintended acceleration,D,3,4,3,SC-001,Highway driving,SG-001,Prevent unintended acceleration >2 m/s²,D
H-002,Loss of braking,D,3,4,3,SC-001,Highway driving,SG-002,Maintain braking force within 10% of commanded,D
```

**fmea_example.csv:**
```csv
fmea_id,function_id,failure_mode,cause,effect,detection,severity,occurrence,rpn,hazard_id
FMEA-001,F-001,Gate driver short circuit,Component wear,Loss of torque control,Built-in self-test,8,3,240,H-001
FMEA-002,F-002,Sensor drift,Temperature exposure,Incorrect torque calculation,Plausibility check,7,4,224,H-001
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Target Coverage:** >80%

**Test Categories:**
- **Pydantic Models:** Validate all validation rules (ASIL values, RPN ranges, ID patterns)
- **Cypher Queries:** Test with mock Neo4j or test database
- **Service Layer:** Test business logic in isolation
- **Utilities:** Test CSV parsing, data transformation

**Example Tests:**
```python
def test_hazard_model_valid_asil():
    """Test Hazard model accepts valid ASIL values"""
    hazard = HazardSchema(id="H-001", description="Test", asil="D")
    assert hazard.asil == "D"

def test_hazard_model_invalid_asil():
    """Test Hazard model rejects invalid ASIL values"""
    with pytest.raises(ValidationError):
        HazardSchema(id="H-001", description="Test", asil="X")

def test_import_hara_creates_nodes(test_db):
    """Test HARA import creates correct nodes"""
    data = HARAImportRequest(hazards=[...], safety_goals=[...])
    result = import_service.import_hara(data)
    assert result.hazards_created == 1
    assert result.safety_goals_created == 1
```

### 8.2 Integration Tests

**Test Categories:**
- **End-to-End Import:** Import seed data, verify all nodes and relationships created
- **Query Accuracy:** Import known data, verify coverage analysis returns expected results
- **Error Handling:** Test duplicate IDs, invalid data, database failures
- **Transaction Rollback:** Test that failed imports don't leave partial data

**Example Tests:**
```python
@pytest.mark.integration
def test_full_import_workflow(client, test_db):
    """Test complete import workflow"""
    # Import HARA
    response = client.post("/import/hara", json=hara_data)
    assert response.status_code == 200

    # Import FMEA
    response = client.post("/import/fmea", json=fmea_data)
    assert response.status_code == 200

    # Verify coverage
    response = client.get("/analytics/hazard-coverage")
    assert response.status_code == 200
    coverage = response.json()
    assert coverage["data"]["summary"]["total"] == 5
```

### 8.3 API Tests

**Test Categories:**
- **Happy Path:** Valid requests return 200 with correct data
- **Validation Errors:** Invalid requests return 400 with detailed errors
- **Not Found:** Requests for non-existent resources return 404
- **Server Errors:** Database failures return 500 with error ID
- **Rate Limiting:** Excessive requests return 429

**Example Tests:**
```python
def test_import_hara_success(client):
    """Test successful HARA import"""
    response = client.post("/import/hara", json=valid_hara_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "hazards_created" in data["data"]

def test_import_hara_invalid_asil(client):
    """Test HARA import with invalid ASIL"""
    invalid_data = {
        "hazards": [{"id": "H-001", "description": "Test", "asil": "X"}],
        "scenarios": [],
        "safety_goals": []
    }
    response = client.post("/import/hara", json=invalid_data)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "asil" in str(data["errors"])
```

### 8.4 Performance Tests

**Test Categories:**
- **Import Speed:** 1000 nodes in <10 seconds
- **Query Speed:** Coverage analysis in <1 second
- **Concurrent Requests:** 100 concurrent requests without errors
- **Large Graph:** Test with 10K+ nodes

**Tools:**
- pytest-benchmark for microbenchmarks
- Locust or Apache Bench for load testing

---

## 9. Deployment

### 9.1 Docker Compose Configuration

**Services:**
1. **Neo4j** (official image)
   - Ports: 7474 (HTTP), 7687 (Bolt)
   - Volumes: neo4j_data, neo4j_logs
   - Environment: NEO4J_AUTH, APOC plugin enabled

2. **Backend** (custom image)
   - Ports: 8000
   - Depends on: Neo4j
   - Environment: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
   - Health check: curl localhost:8000/health

**Example docker-compose.yml:**
```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/safetygraph123
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "safetygraph123", "RETURN 1"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=safetygraph123
    depends_on:
      neo4j:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  neo4j_data:
  neo4j_logs:
```

### 9.2 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| NEO4J_URI | Neo4j connection URI | bolt://localhost:7687 | Yes |
| NEO4J_USER | Neo4j username | neo4j | Yes |
| NEO4J_PASSWORD | Neo4j password | - | Yes |
| API_HOST | API server host | 0.0.0.0 | No |
| API_PORT | API server port | 8000 | No |
| LOG_LEVEL | Logging level | INFO | No |
| CORS_ORIGINS | Allowed CORS origins | * | No |

### 9.3 Startup Procedure

1. Start Neo4j and wait for health check
2. Run schema initialization (create constraints and indexes)
3. Start FastAPI backend
4. Verify backend health check passes
5. (Optional) Import seed data

**Initialization Script:**
```bash
#!/bin/bash
set -e

echo "Waiting for Neo4j..."
until curl -s http://localhost:7474 > /dev/null; do
  sleep 2
done

echo "Initializing Neo4j schema..."
cypher-shell -u neo4j -p safetygraph123 < /data/schema/neo4j_constraints.cypher

echo "Starting backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000

echo "Importing seed data..."
python scripts/import_seed_data.py

echo "Safety Graph Twin is ready!"
```

---

## 10. Success Criteria

### 10.1 Functional Criteria

- [ ] All 4 import endpoints accept valid data and create correct nodes/relationships
- [ ] Hazard coverage analysis correctly identifies full/partial/no coverage
- [ ] Impact analysis traverses graph and returns all affected artifacts
- [ ] Gap analysis identifies missing links in safety chain
- [ ] Statistics endpoint returns accurate counts and percentages
- [ ] All validation errors return clear, actionable messages

### 10.2 Performance Criteria

- [ ] Import 1000 nodes in <10 seconds
- [ ] Coverage analysis completes in <1 second (P95)
- [ ] Impact analysis completes in <1 second (P95)
- [ ] API handles 100 concurrent requests without errors
- [ ] Database queries use indexes (verified with EXPLAIN)

### 10.3 Quality Criteria

- [ ] >80% test coverage on core logic
- [ ] All tests pass (unit, integration, API)
- [ ] Code passes linting (Ruff) and formatting (Black)
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] OpenAPI documentation is complete and accurate

### 10.4 Usability Criteria

- [ ] Non-expert can run demo in <30 minutes using README
- [ ] Seed data import script works without manual intervention
- [ ] Docker Compose starts full stack with single command
- [ ] API documentation includes cURL examples
- [ ] Error messages are clear and actionable

### 10.5 Acceptance Criteria

**Demo Scenario:**
1. Start system with `docker-compose up`
2. Import seed data (EV inverter example)
3. Run coverage analysis - identifies 1 hazard with no coverage
4. Run impact analysis on "Gate Driver" component - shows all affected hazards
5. Manually verify results against expected output

**Acceptance Test:**
- Safety engineer can identify all ASIL-D hazards without test coverage
- Systems engineer can determine impact of changing "Inverter Controller" component
- Results match manual analysis (100% accuracy on seed data)

---

## 11. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Neo4j performance with large graphs | High | Medium | Add indexes, optimize queries, consider Memgraph for v2 |
| Complex Cypher queries hard to maintain | Medium | High | Extract queries to separate module, add comprehensive tests, document patterns |
| Import data quality varies | High | High | Strict Pydantic validation, clear error messages, provide validation scripts |
| Schema changes break existing data | High | Low | Version schema, provide migration scripts, maintain backward compatibility where possible |
| Database downtime during import | Medium | Low | Implement transactional imports, add retry logic, provide import resume capability |
| User provides malformed CSV | Medium | High | Validate CSV structure before parsing, provide CSV templates, clear error messages |

---

## 12. Future Considerations (Out of Scope for Phase 1)

**Deferred to Later Phases:**
- Runtime defect integration (Phase 3)
- Advanced analytics (centrality, weak link detection) (Phase 4)
- Frontend UI (Phase 2)
- Authentication/authorization
- Multi-user support
- Audit trails
- Change tracking
- SysML XMI import

**Technical Debt to Address:**
- Replace mock/placeholder logic with production implementations
- Optimize queries based on real-world usage patterns
- Add comprehensive logging and monitoring
- Implement caching for expensive queries

---

## 13. Appendix

### 13.1 Glossary

See `claude.md` for full glossary.

### 13.2 References

- ISO 26262:2018 - Road vehicles — Functional safety
- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Pydantic Documentation: https://docs.pydantic.dev/

### 13.3 Related Documents

- `claude.md` - Project context and guidelines
- `TODO.md` - Implementation task list
- `prd-phase2.md` - Frontend & Visualization PRD
- `prd-phase3.md` - Runtime Defects PRD
- `prd-phase4.md` - Advanced Analytics PRD

---

**Document Status:** Draft
**Last Updated:** 2025-11-18
**Next Review:** After M1 completion
**Owner:** Product/Engineering Team
