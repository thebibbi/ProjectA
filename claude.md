# Safety Graph Twin - Project Context for AI Assistants

## Project Overview

**Project Name:** Safety Graph Twin
**Version:** 1.0 (Planning Phase)
**Domain:** Automotive/Robotics Safety Engineering
**Compliance:** ISO 26262 (Functional Safety), ISO 21434 (Cybersecurity)

### Mission Statement

Build a knowledge graph system that unifies safety-critical automotive/robotics system documentation to enable impact analysis, coverage tracking, and runtime monitoring aligned with ISO 26262 safety standards.

### Core Value Proposition

The Safety Graph Twin breaks down data silos between safety artifacts by creating an interconnected graph database linking:
- System architecture (SysML-style blocks, functions, signals)
- Safety artifacts (HARA, SOTIF, hazards, ASIL ratings)
- Safety analyses (FMEA, FTA, FMEDA)
- Requirements and test cases with full traceability
- Field defects and runtime events

This enables critical safety questions like:
- "Which ASIL-D safety goals are supported only by a single mitigation with weak test coverage?"
- "A defect appeared on inverter gate driver X – which hazards, safety goals and tests are impacted?"
- "Where are gaps between FMEA → FTA → test evidence?"

---

## Technology Stack (SOTA 2025)

### Backend

- **Graph Database:** Neo4j 5.x (Community or Enterprise)
  - *Alternative:* Memgraph (8-50x faster, consider for v2 if performance critical)
  - Query Language: Cypher
  - Driver: Official Neo4j Python Driver 5.x

- **Application Framework:** Python 3.11+ with FastAPI 0.115+
  - Async/await support for high concurrency
  - Native Pydantic v2 integration for validation
  - OpenAPI/Swagger auto-documentation

- **Dependency Management:** Poetry 1.8+
  - Reproducible builds
  - Virtual environment management
  - Dependency resolution

- **Data Validation:** Pydantic v2
  - Type-safe schemas with Python type hints
  - Rust-based core for 2.5x performance vs alternatives
  - Seamless FastAPI integration

### Frontend

- **Framework:** React 18+ with TypeScript 5+
  - Build Tool: Vite 5+ (fast HMR, optimal bundling)
  - State Management: React Query (TanStack Query v5) for server state
  - Local State: Zustand or React Context API

- **Graph Visualization:**
  - **Primary:** ReactFlow (XyFlow) - Modern, interactive node-based UI
  - **Alternative:** Cytoscape.js - Powerful for complex graph layouts
  - Both support custom styling, interactions, and layout algorithms

- **UI Components:** shadcn/ui or Material-UI (MUI)
  - TypeScript-native components
  - Accessible (WCAG compliant)
  - Customizable theming

### Graph Analytics

- **Python Libraries:**
  - **igraph-python:** 13-250x faster than NetworkX for centrality algorithms
  - **APOC** (Neo4j plugin): Graph algorithms within Cypher
  - **Neo4j Graph Data Science (GDS):** Enterprise-grade graph ML
  - **PFTA/SFTA:** Fault Tree Analysis in Python

### Data Ingestion & ETL

- **Initial Format:** CSV/YAML/JSON
  - pandas for data manipulation
  - PyYAML for YAML parsing
  - CSV validation with Pydantic

- **Future SysML Support:**
  - **Challenge:** XMI parsers for Python are outdated/tool-specific
  - **Options:**
    - xmiparser (outdated - UML 1.2)
    - Custom parser using lxml/ElementTree
    - PySysML2 (for SysML v2 textual format)
  - **Recommendation:** Focus on CSV/YAML for v1, revisit SysML in v2

### Deployment & DevOps

- **Containerization:** Docker + Docker Compose
  - Neo4j container (official image)
  - FastAPI backend container
  - React frontend container (nginx for production)
  - Volume management for data persistence

- **Testing:**
  - **Backend:** pytest + pytest-asyncio
  - **Neo4j Testing:** Docker-based test containers or mocking with CollectingQueryRunner
  - **Frontend:** Vitest + React Testing Library
  - **E2E:** Playwright or Cypress

- **Code Quality:**
  - Black (formatting)
  - Ruff (linting - faster than Flake8)
  - mypy (type checking)
  - pre-commit hooks

---

## Graph Schema Design

### Node Types (12 categories)

**Architecture Nodes:**
- `Item` - High-level system/subsystem (e.g., "HV Battery System")
- `Function` - Logical/functional block (e.g., "Torque Control")
- `Component` - Concrete HW/SW element (ECU, sensor, inverter, SW module)
- `Signal` - Logical or physical signal (e.g., TorqueCmd, WheelSpeed_FL)

**Safety Nodes:**
- `Hazard` - Hazardous event description
- `Scenario` - Operating scenario / ODD slice (SOTIF/ADS)
- `SafetyGoal` - From HARA analysis
- `FunctionalSafetyRequirement` (FSR) - High-level safety requirements
- `TechnicalSafetyRequirement` (TSR) - Implementation-level requirements

**Analysis Nodes:**
- `FMEAEntry` - FMEA analysis entry
- `FailureMode` - Specific failure mode (can be shared across FMEA entries)
- `FTEvent` - Fault Tree events (basic, intermediate, top)

**Verification Nodes:**
- `TestCase` - Test/validation artifact

**Runtime Nodes:**
- `DefectInstance` / `FieldEvent` - Runtime issues from field/production

**Compliance Nodes (Optional):**
- `StandardClause` - ISO 26262 / ISO 21434 clauses

### Relationship Types

**Architecture Relationships:**
- `(Item)-[:HAS_FUNCTION]->(Function)`
- `(Function)-[:REALIZED_BY]->(Component)`
- `(Function)-[:USES_SIGNAL]->(Signal)`
- `(Component)-[:CONNECTED_TO]->(Component)`

**Safety Concept Relationships:**
- `(Hazard)-[:IN_SCENARIO]->(Scenario)`
- `(Hazard)-[:MITIGATED_BY]->(SafetyGoal)`
- `(SafetyGoal)-[:REFINED_INTO]->(FunctionalSafetyRequirement)`
- `(FunctionalSafetyRequirement)-[:ALLOCATED_TO]->(Item|Function|Component)`

**Analysis Relationships:**
- `(FMEAEntry)-[:FOR_FUNCTION]->(Function)`
- `(FMEAEntry)-[:HAS_FAILURE_MODE]->(FailureMode)`
- `(FailureMode)-[:CAN_LEAD_TO]->(Hazard)`
- `(FTEvent)-[:CAUSES]->(FTEvent)`
- `(FTEvent)-[:ASSOCIATED_WITH]->(FailureMode|Component)`

**Verification Relationships:**
- `(FunctionalSafetyRequirement|TechnicalSafetyRequirement)-[:VERIFIED_BY]->(TestCase)`
- `(TestCase)-[:COVERS_SIGNAL]->(Signal)`

**Runtime Relationships:**
- `(DefectInstance)-[:OBSERVED_AT]->(Component)`
- `(DefectInstance)-[:INSTANCE_OF]->(FailureMode)`
- `(DefectInstance)-[:RELATED_TO]->(Hazard)`

---

## Project Phases & Scope

### Version 1: "Design & Analysis Graph"

**Goal:** Static lifecycle artifact analysis

**Capabilities:**
- Import architecture models (YAML/JSON)
- Import HARA entries (Hazard, Operating Scenario, ASIL, Safety Goal)
- Import FMEA entries (Item, Function, Failure Mode, Cause, Effect, Detection, RPN)
- Import FTA structures (basic events, gates, top events)
- Import Requirements & test cases (IDs and trace links)
- Change impact queries
- Coverage/gap analysis (hazard→goal→requirement→test)
- Centrality metrics to identify safety-critical hubs

### Version 2: "Closed Loop Safety Graph"

**Goal:** Runtime monitoring integration

**Capabilities:**
- Ingest runtime defects/events (CV anomalies, warranty claims)
- Link DefectInstance → (Component, FailureMode, Hazard, SafetyGoal)
- Discrepancy analysis:
  - Hazards with many real defects but low risk rating
  - Requirements with passing tests but correlated with field incidents

---

## Implementation Milestones

### M1: Core KG & ETL (Backend Foundation)

**Deliverables:**
1. Neo4j schema definition with constraints and indexes
2. FastAPI service with endpoints:
   - `POST /import/hara` - Import HARA analysis
   - `POST /import/fmea` - Import FMEA entries
   - `POST /import/requirements` - Import FSR/TSR and allocations
   - `POST /import/tests` - Import test cases and verification links
3. Core Cypher queries:
   - Hazard coverage query
   - Component impact analysis
4. Docker Compose configuration
5. Seed data (example CSV files)

**Duration Estimate:** 2-3 weeks for AI-assisted development

### M2: Frontend & Visualization

**Deliverables:**
1. React + TypeScript application
2. Pages/Views:
   - Hazard Coverage Dashboard (table with status)
   - Drilldown view (hazard → goals → requirements → tests chain)
   - Impact Explorer (graph visualization of component neighborhood)
3. Integration with backend API
4. Graph visualization using ReactFlow or Cytoscape.js

**Duration Estimate:** 2-3 weeks

### M3: Runtime Defects Integration

**Deliverables:**
1. `POST /import/defects` endpoint
2. DefectInstance node type and relationships
3. Discrepancy analysis endpoint:
   - `GET /analytics/discrepancy` - Predicted risk vs observed defects

**Duration Estimate:** 1-2 weeks

### M4: Advanced Graph Analytics

**Deliverables:**
1. Centrality metrics implementation (betweenness, eigenvector)
2. Using igraph or Neo4j GDS
3. Preliminary FT synthesis from KG patterns
4. Weak link detection algorithm

**Duration Estimate:** 2-3 weeks

---

## Key Analytics & Queries

### 1. Coverage Analysis
Find `Hazard` nodes not connected to any `TestCase` through the chain:
```cypher
MATCH (h:Hazard)
WHERE NOT (h)-[:MITIGATED_BY]->(:SafetyGoal)-[:REFINED_INTO]->
          (:FunctionalSafetyRequirement)-[:VERIFIED_BY]->(:TestCase)
RETURN h
```

### 2. Weak Link Detection
Find Components/Functions with high betweenness centrality:
- High betweenness = single point of safety failure
- Changes here trigger extensive impact analysis

### 3. Change Impact Analysis
Given a modified Component, traverse:
```cypher
MATCH (c:Component {id: $component_id})
MATCH path = (c)-[*1..4]-(related)
WHERE related:FailureMode OR related:FMEAEntry OR
      related:FTEvent OR related:Hazard OR
      related:SafetyGoal OR related:TestCase
RETURN DISTINCT related, path
```

### 4. Design vs Runtime Discrepancy
Compare observed defect rates vs HARA risk estimates:
```cypher
MATCH (h:Hazard)<-[:RELATED_TO]-(d:DefectInstance)
WITH h, count(d) as defect_count
WHERE h.asil IN ['C', 'D'] AND defect_count > threshold
RETURN h, defect_count
ORDER BY defect_count DESC
```

---

## API Design Principles

### RESTful Endpoints

**Import Operations:**
- `POST /import/hara` - Upload HARA analysis
- `POST /import/fmea` - Upload FMEA data
- `POST /import/requirements` - Upload requirements
- `POST /import/tests` - Upload test cases
- `POST /import/defects` - Upload defect instances (v2)

**Analytics Operations:**
- `GET /analytics/hazard-coverage` - Get coverage status for all hazards
- `GET /analytics/impact/component/{component_id}` - Impact analysis
- `GET /analytics/weak-links` - Find safety-critical hubs (M4)
- `GET /analytics/discrepancy` - Design vs runtime analysis (M3)

**Query Operations (Optional Power-User Feature):**
- `POST /query/cypher` - Execute custom Cypher query (with safety limits)

### Data Formats

**Request Format:** JSON with Pydantic validation
**Response Format:** JSON with standardized structure:
```json
{
  "status": "success" | "error",
  "data": { ... },
  "message": "Human-readable message",
  "meta": {
    "timestamp": "ISO 8601",
    "query_time_ms": 123
  }
}
```

---

## Development Guidelines

### Code Organization

```
ProjectA/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── import_routes.py
│   │   │   │   ├── analytics_routes.py
│   │   │   │   └── query_routes.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── neo4j_driver.py
│   │   │   ├── schema.py
│   │   │   └── queries.py
│   │   ├── models/
│   │   │   ├── nodes.py
│   │   │   ├── relationships.py
│   │   │   └── schemas.py (Pydantic)
│   │   ├── services/
│   │   │   ├── import_service.py
│   │   │   └── analytics_service.py
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── data/
│   ├── seed/
│   │   ├── hara_example.csv
│   │   ├── fmea_example.csv
│   │   └── requirements_example.csv
│   └── schema/
│       └── neo4j_constraints.cypher
├── docker-compose.yml
├── README.md
├── claude.md (this file)
├── TODO.md
└── docs/
    └── prds/
        ├── prd-phase1.md
        ├── prd-phase2.md
        ├── prd-phase3.md
        └── prd-phase4.md
```

### Coding Standards

**Python:**
- Type hints everywhere (`def func(x: int) -> str:`)
- Docstrings in Google format
- Max line length: 100 characters
- Use async/await for I/O operations
- Pydantic for all data validation

**TypeScript:**
- Strict mode enabled
- Functional components with hooks
- Type everything (no `any` without justification)
- Use interfaces for object shapes

**Cypher:**
- Use parameters for all dynamic values (prevent injection)
- Add indexes for frequently queried properties
- Use `EXPLAIN` and `PROFILE` for query optimization

---

## Important Constraints & Considerations

### ISO 26262 Context

**CRITICAL:** Python is NOT suitable for implementing safety-critical automotive software (ASIL B-D). ISO 26262 restricts to C (MISRA C), Ada (SPARK), or similar proven languages.

**This project's scope:** Documentation, analysis, research, and knowledge management - NOT runtime safety-critical code.

### Data Privacy & Security

- No PII (Personally Identifiable Information) in defect data
- Consider authentication/authorization for production deployments
- Field data may contain proprietary information - access control required

### Performance Considerations

- **Small graphs (<10K nodes):** NetworkX acceptable
- **Medium graphs (10K-1M nodes):** Use igraph or Neo4j APOC
- **Large graphs (>1M nodes):** Consider Memgraph or Neo4j Enterprise with GDS

### SysML Import Challenges

- XMI format varies by tool (Cameo, Capella, Rhapsody, etc.)
- No universal Python parser for modern SysML
- **Strategy:** Focus on CSV/YAML for v1, build custom SysML parser only if specific tool identified

---

## References & Prior Art

### Academic & Industry Work

1. **SafetyLens (VIS 2020):** Visualization of hazard-requirement-test linkages for ISO 26262
2. **Knowledge graph approaches:** Unifying FMEA, HAZOP, FTA, bow-tie analysis
3. **Model-based safety analysis:** SysML + automatic FTA generation
4. **Fault tree synthesis:** Recent work on generating FT from structural/functional KG
5. **GENIAL! Basic Ontology (GBO):** ISO 26262-based ontology for cyber-physical systems

### Tools & Libraries

- **EMFTA:** Eclipse-based open source fault tree analysis tool (Java)
- **PFTA/SFTA:** Python fault tree analysis libraries
- **ReqTIFy:** Requirements traceability tool (commercial)

---

## Success Metrics

### Phase 1 Success Criteria

- [ ] Successfully import sample HARA with 10+ hazards
- [ ] Successfully import sample FMEA with 20+ entries
- [ ] Import requirements and tests with full traceability
- [ ] Coverage analysis identifies at least one gap
- [ ] Impact analysis traces from component to all affected artifacts
- [ ] Documentation allows non-expert to run demo in <30 minutes

### Phase 2 Success Criteria

- [ ] Interactive graph visualization renders 100+ node graphs smoothly
- [ ] Drilldown view shows complete hazard→test chains
- [ ] UI loads in <2 seconds, queries complete in <1 second

### Long-term Success

- Becomes the "single source of truth" for safety artifact relationships
- Reduces time to perform impact analysis from days to minutes
- Identifies previously unknown safety coverage gaps
- Integrates into CI/CD to catch breaking changes before release

---

## Getting Started (For AI Assistants)

When beginning work on this project:

1. **Read this file completely** to understand context
2. **Review TODO.md** for current task priorities
3. **Check relevant PRD** in `docs/prds/` for detailed requirements
4. **Follow the tech stack** - don't introduce new dependencies without justification
5. **Write tests** - aim for >80% coverage on critical paths
6. **Document as you code** - update README.md with setup instructions
7. **Ask questions** - safety-critical domains have nuances, clarify before assuming

---

## Glossary

- **ASIL:** Automotive Safety Integrity Level (A=lowest, D=highest)
- **FMEA:** Failure Mode and Effects Analysis
- **FTA:** Fault Tree Analysis
- **FMEDA:** Failure Mode Effects and Diagnostic Analysis
- **FSR:** Functional Safety Requirement
- **HARA:** Hazard Analysis and Risk Assessment
- **SOTIF:** Safety Of The Intended Functionality
- **TSR:** Technical Safety Requirement
- **RPN:** Risk Priority Number (Severity × Occurrence × Detection)
- **ODD:** Operational Design Domain
- **KG:** Knowledge Graph
- **SysML:** Systems Modeling Language
- **XMI:** XML Metadata Interchange

---

**Last Updated:** 2025-11-18
**Project Status:** Planning Phase
**Next Milestone:** M1 - Core KG & ETL
