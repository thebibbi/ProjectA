# Product Requirements Document: Phase 4 - Advanced Graph Analytics

**Project:** Safety Graph Twin
**Phase:** M4 - Advanced Graph Analytics
**Version:** 1.0
**Date:** 2025-11-18
**Status:** Planning
**Dependencies:** Phase 1 (Core KG & ETL), Phase 2 (Frontend), Phase 3 (Defects) should be complete

---

## 1. Executive Summary

### 1.1 Overview

Phase 4 introduces advanced graph analytics capabilities to the Safety Graph Twin, leveraging graph algorithms and network analysis to identify safety-critical architectural patterns, weak links, and hidden dependencies. This phase also includes preliminary fault tree synthesis from knowledge graph patterns, automating tedious manual FTA construction.

### 1.2 Business Value

**Key Capabilities:**
- **Weak Link Detection:** Identify components that are single points of safety failure
- **Critical Path Analysis:** Find shortest paths from failures to hazards
- **Centrality Metrics:** Rank components by safety criticality using graph algorithms
- **Fault Tree Synthesis:** Auto-generate fault trees from KG patterns
- **Change Impact Prediction:** Predict blast radius of architectural changes

**ROI:**
- Reduce time to identify critical components from weeks to minutes
- Automate FTA generation (save 40-60 hours per hazard)
- Enable proactive architecture reviews before design freeze
- Improve resource allocation (focus testing on high-centrality components)

### 1.3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Centrality Calculation Time | <10 seconds for 10K node graph | Benchmark |
| Weak Link Detection Accuracy | >95% vs expert analysis | Validation with domain experts |
| FT Synthesis Coverage | >80% of manual FT structure | Comparison with hand-built FTs |
| User Decision Speed | 10x faster critical component identification | User testing |

---

## 2. Problem Statement

### 2.1 Current Pain Points

**For Safety Architects:**
- No automated way to identify which components are safety-critical "hubs"
- Must manually review architecture diagrams to find single points of failure
- Fault tree analysis is time-consuming (40-60 hours per top event)
- Difficult to assess impact of architecture changes on safety

**For Safety Engineers:**
- Cannot easily find all paths from component to hazards
- No quantitative metric for "how critical is this component?"
- FTA requires manual construction and maintenance
- Changes to system architecture invalidate existing FTAs

**For Program Managers:**
- Cannot prioritize safety investments based on quantitative criticality
- No visibility into architectural weak points before incidents occur

### 2.2 User Stories

**US1:** As a safety architect, I want to see which components have the highest betweenness centrality, so I can identify single points of safety failure.

**US2:** As a safety engineer, I want to automatically generate a fault tree for a hazard, so I can save time and ensure completeness.

**US3:** As a systems engineer, I want to simulate removing a component and see the impact, so I can evaluate architectural alternatives.

**US4:** As a program manager, I want a ranked list of safety-critical components, so I can allocate testing resources effectively.

---

## 3. Requirements

### 3.1 Functional Requirements

#### FR1: Graph Centrality Metrics

**FR1.1 Betweenness Centrality**
- MUST calculate betweenness centrality for Component and Function nodes
- Definition: Proportion of shortest paths between node pairs that pass through this node
- High betweenness = "bridge" node = single point of failure
- MUST rank nodes by betweenness
- SHOULD filter to safety-relevant paths only (paths touching Hazard or SafetyGoal nodes)

**FR1.2 Eigenvector Centrality (or PageRank)**
- SHOULD calculate eigenvector centrality or PageRank for Component nodes
- Definition: Importance based on importance of connected nodes
- High eigenvector centrality = connected to other important nodes

**FR1.3 Degree Centrality**
- MUST calculate degree centrality (number of connections)
- Useful for identifying highly connected hubs
- Distinguish in-degree vs out-degree for directed relationships

**FR1.4 Closeness Centrality**
- SHOULD calculate closeness centrality
- Definition: Average shortest path length to all other nodes
- High closeness = can quickly affect many other nodes

**FR1.5 Calculation Trigger**
- MUST provide `POST /analytics/calculate-metrics` endpoint to trigger calculation
- Calculation SHOULD be asynchronous for large graphs (>5K nodes)
- SHOULD cache results (recalculate only when graph changes)
- MUST store metrics as node properties in Neo4j

**FR1.6 Metrics Retrieval**
- MUST provide `GET /analytics/weak-links?metric=betweenness&top=20` endpoint
- MUST return ranked list of components with highest centrality
- MUST include:
  - Component ID, name, type
  - Centrality score
  - Connected hazards (for context)
  - Recommended actions (e.g., "Add redundancy")

#### FR2: Critical Path Analysis

**FR2.1 Shortest Paths**
- MUST provide `GET /analytics/shortest-path?from={node_id}&to={node_id}` endpoint
- MUST find shortest path between two nodes
- SHOULD find all shortest paths (if multiple exist)
- SHOULD support path constraints (e.g., only safety-relevant relationships)

**FR2.2 All Paths from Component to Hazards**
- MUST provide `GET /analytics/component-hazard-paths/{component_id}` endpoint
- MUST find all paths from Component to any Hazard
- MUST limit path length (default: 6 hops)
- MUST rank paths by length and criticality

**FR2.3 Critical Path Visualization**
- Frontend MUST highlight critical paths in graph visualization
- SHOULD use edge thickness or color to indicate criticality
- SHOULD support "show only critical paths" filter

#### FR3: Weak Link Detection

**FR3.1 Single Point of Failure Detection**
- MUST identify components where removal breaks all paths from sources to critical hazards
- Algorithm:
  1. For each Component node
  2. Temporarily remove it (and its edges)
  3. Check if any ASIL-C/D Hazard becomes unreachable from SafetyGoal
  4. If yes, mark as single point of failure
- MUST provide `GET /analytics/single-points-of-failure` endpoint

**FR3.2 Weak Link Ranking**
- MUST combine multiple metrics to rank weak links:
  - Betweenness centrality (weight: 40%)
  - ASIL allocation (weight: 30%)
  - Defect count (weight: 20%, if Phase 3 complete)
  - Redundancy level (weight: 10%)
- MUST provide weakness score (0-100)
- MUST provide actionable recommendations:
  - "Add redundant component"
  - "Increase test coverage"
  - "Review ASIL decomposition"

#### FR4: Fault Tree Synthesis

**FR4.1 Synthesis Algorithm (Preliminary)**
- MUST generate basic fault tree structure from KG patterns
- Algorithm:
  1. Start with Hazard (top event)
  2. Find all FailureModes that CAN_LEAD_TO this Hazard
  3. For each FailureMode, find FMEAEntries and causes
  4. Create FTEvent nodes:
     - Top event = Hazard
     - Intermediate events = FailureModes
     - Basic events = FMEA causes or component failures
  5. Create gate relationships:
     - OR gate if multiple failure modes can cause hazard
     - AND gate if multiple conditions required (infer from relationships)
- MUST create FTEvent nodes and CAUSES relationships

**FR4.2 Synthesis Endpoint**
- MUST provide `POST /analytics/synthesize-ft/{hazard_id}` endpoint
- MUST return FT structure:
  - List of FTEvent nodes (id, type, description, gate_type)
  - List of CAUSES relationships
  - Root event (top)
- SHOULD validate synthesized FT (no cycles, all basic events are leaves)

**FR4.3 FT Visualization**
- Frontend SHOULD render fault tree as hierarchical tree
- SHOULD use standard FT symbols:
  - Rectangle for events
  - Circle for basic events
  - AND/OR gate symbols
- SHOULD support export as image or standard FT format (if applicable)

**FR4.4 Limitations & Future Work**
- Phase 4 v1: Basic OR/AND gates only
- Future: Support priority-AND, XOR, voting gates
- Future: Quantitative analysis (failure probabilities)
- Future: Integration with PFTA/SFTA libraries for full FTA

#### FR5: Architecture Simulation (Optional)

**FR5.1 Component Removal Simulation**
- MAY provide `POST /analytics/simulate-removal/{component_id}` endpoint
- Simulate removing component from graph
- Return:
  - Hazards that become unreachable
  - Requirements that lose verification
  - Orphaned tests
- Useful for "what if we remove this sensor?" analysis

**FR5.2 Component Addition Simulation**
- MAY provide `POST /analytics/simulate-addition` endpoint
- Simulate adding new component and relationships
- Return:
  - Impact on coverage
  - Impact on centrality metrics
- Useful for architecture trade studies

### 3.2 Non-Functional Requirements

**NFR1: Performance**
- Centrality calculation: <10 seconds for 10K nodes (using igraph or Neo4j GDS)
- Shortest path: <500ms for typical graph
- FT synthesis: <5 seconds for hazard with 50 failure modes

**NFR2: Scalability**
- Support graphs up to 100K nodes (Phase 4 v1)
- Use batch processing for very large graphs
- Provide progress indication for long-running calculations

**NFR3: Accuracy**
- Centrality calculations MUST match standard algorithms (validate against NetworkX/igraph)
- FT synthesis MUST produce valid fault trees (no cycles, correct gate logic)

---

## 4. Technical Design

### 4.1 Implementation Options

#### Option A: Python igraph (Recommended for Phase 4)

**Pros:**
- 13-250x faster than NetworkX for centrality
- Rich set of algorithms (betweenness, PageRank, shortest paths)
- Python API, easy to integrate with FastAPI
- No additional infrastructure

**Cons:**
- Requires exporting Neo4j graph to igraph format
- Metrics must be written back to Neo4j

**Implementation:**
```python
import igraph as ig
from neo4j import GraphDatabase

def calculate_centrality_metrics():
    # 1. Export Neo4j graph to igraph
    graph = export_neo4j_to_igraph()

    # 2. Calculate metrics
    betweenness = graph.betweenness()
    pagerank = graph.pagerank()

    # 3. Write back to Neo4j
    write_metrics_to_neo4j(betweenness, pagerank)
```

#### Option B: Neo4j Graph Data Science (GDS)

**Pros:**
- Native Neo4j integration (no export needed)
- Extremely fast (optimized for Neo4j)
- Support for graph projections (in-memory subgraphs)

**Cons:**
- Requires Neo4j Enterprise (or GDS plugin in Community)
- More complex setup
- Licensing considerations for production

**Implementation:**
```cypher
// Create graph projection
CALL gds.graph.project(
  'safety-graph',
  ['Component', 'Function', 'Hazard', 'SafetyGoal'],
  ['REALIZED_BY', 'HAS_FUNCTION', 'MITIGATED_BY']
)

// Calculate betweenness
CALL gds.betweenness.stream('safety-graph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS component_id, score
ORDER BY score DESC
```

**Recommendation:** Use igraph for Phase 4 v1 (simpler, no licensing issues). Consider GDS for Phase 4 v2 if performance becomes critical.

### 4.2 Fault Tree Synthesis Algorithm

**Detailed Algorithm:**

```python
def synthesize_fault_tree(hazard_id: str) -> FaultTree:
    # Step 1: Create top event (Hazard)
    top_event = FTEvent(
        id=f"FT-TOP-{hazard_id}",
        type="top",
        description=hazard.description,
        gate_type=None
    )

    # Step 2: Find all failure modes that can lead to this hazard
    failure_modes = query(
        "MATCH (fm:FailureMode)-[:CAN_LEAD_TO]->(h:Hazard {id: $hazard_id}) RETURN fm",
        hazard_id=hazard_id
    )

    if len(failure_modes) == 0:
        raise ValueError("No failure modes linked to hazard")

    # Step 3: Create intermediate event (OR gate for multiple failure modes)
    if len(failure_modes) > 1:
        intermediate_event = FTEvent(
            id=f"FT-INT-{hazard_id}",
            type="intermediate",
            description=f"Any failure mode causing {hazard.description}",
            gate_type="OR"
        )
        create_relationship(top_event, "CAUSES", intermediate_event)
    else:
        intermediate_event = top_event  # Single failure mode, no intermediate gate

    # Step 4: For each failure mode, create basic or intermediate events
    for fm in failure_modes:
        # Find FMEA entries for this failure mode
        fmea_entries = query(
            "MATCH (fmea:FMEAEntry)-[:HAS_FAILURE_MODE]->(fm:FailureMode {name: $fm_name}) RETURN fmea",
            fm_name=fm.name
        )

        if len(fmea_entries) == 0:
            # No FMEA details, create basic event directly
            basic_event = FTEvent(
                id=f"FT-BASIC-{fm.name}",
                type="basic",
                description=fm.name,
                gate_type=None
            )
            create_relationship(intermediate_event, "CAUSES", basic_event)
        else:
            # Create intermediate event for this failure mode
            fm_event = FTEvent(
                id=f"FT-FM-{fm.name}",
                type="intermediate",
                description=fm.description,
                gate_type="OR"  # Assume OR for multiple causes
            )
            create_relationship(intermediate_event, "CAUSES", fm_event)

            # Create basic events for each cause
            for fmea in fmea_entries:
                cause_event = FTEvent(
                    id=f"FT-CAUSE-{fmea.id}",
                    type="basic",
                    description=fmea.cause,
                    gate_type=None
                )
                create_relationship(fm_event, "CAUSES", cause_event)

    return FaultTree(top_event=top_event, events=all_events, relationships=all_rels)
```

**Limitations:**
- Assumes OR gates (conservative approach)
- Does not infer AND gates (requires domain knowledge or annotations)
- Does not calculate failure probabilities (requires additional data)

**Future Enhancements:**
- Use FMEA detection methods to infer AND gates (if detection is "AND of X and Y")
- Integrate with PFTA/SFTA for quantitative analysis
- Allow user to refine auto-generated FT via UI

### 4.3 Data Model Extensions

**New Node Properties:**
```cypher
// Add centrality metrics to Component nodes
(Component {
  betweenness_centrality: float,
  pagerank: float,
  degree_centrality: int,
  closeness_centrality: float,
  weakness_score: float,  // composite score
  is_single_point_of_failure: boolean,
  metrics_updated_at: datetime
})
```

**New Nodes:**
```cypher
// Fault Tree Event nodes (if persisting FT in graph)
(:FTEvent {
  id: string,
  type: string,  // 'top', 'intermediate', 'basic'
  description: string,
  gate_type: string  // 'AND', 'OR', 'XOR', etc.
})
```

**New Relationships:**
```cypher
(FTEvent)-[:CAUSES]->(FTEvent)
(FTEvent)-[:ASSOCIATED_WITH]->(FailureMode|Component)
```

---

## 5. API Specification

### 5.1 Calculate Metrics

**Endpoint:** `POST /analytics/calculate-metrics`

**Request:**
```json
{
  "metrics": ["betweenness", "pagerank", "degree"],
  "node_types": ["Component", "Function"],
  "async": true  // Optional, for large graphs
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "metrics-job-12345",  // If async=true
    "estimated_time_seconds": 45
  },
  "message": "Metrics calculation started. Check /analytics/metrics-job/metrics-job-12345 for status."
}
```

**Response (sync):**
```json
{
  "status": "success",
  "data": {
    "metrics_calculated": ["betweenness", "pagerank", "degree"],
    "nodes_analyzed": 523,
    "calculation_time_seconds": 8.3
  }
}
```

### 5.2 Get Weak Links

**Endpoint:** `GET /analytics/weak-links?metric=betweenness&top=20&min_asil=C`

**Response:**
```json
{
  "status": "success",
  "data": {
    "weak_links": [
      {
        "component_id": "C-INV-001",
        "component_name": "Inverter Controller",
        "betweenness_centrality": 0.78,
        "pagerank": 0.045,
        "weakness_score": 87.5,
        "is_single_point_of_failure": true,
        "connected_hazards": [
          {"id": "H-001", "asil": "D"},
          {"id": "H-005", "asil": "C"}
        ],
        "defect_count": 23,  // If Phase 3 complete
        "recommendations": [
          "Add redundant controller (hot standby)",
          "Increase test coverage to 100% MC/DC",
          "Review ASIL decomposition for allocated requirements"
        ]
      },
      {
        "component_id": "C-BMS-001",
        "component_name": "Battery Management System",
        "betweenness_centrality": 0.65,
        "pagerank": 0.038,
        "weakness_score": 78.2,
        "is_single_point_of_failure": false,
        "connected_hazards": [
          {"id": "H-015", "asil": "D"}
        ],
        "defect_count": 12,
        "recommendations": [
          "Monitor closely - high centrality but redundancy exists"
        ]
      }
    ],
    "summary": {
      "total_components_analyzed": 150,
      "single_points_of_failure_count": 3,
      "high_weakness_count": 12  // score > 70
    }
  }
}
```

### 5.3 Synthesize Fault Tree

**Endpoint:** `POST /analytics/synthesize-ft/{hazard_id}`

**Request Body (optional):**
```json
{
  "options": {
    "include_all_causes": true,  // Include all FMEA causes or limit to top RPN
    "max_depth": 5,  // Maximum FT depth
    "persist_to_graph": true  // Store FTEvent nodes in Neo4j
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "hazard_id": "H-001",
    "hazard_description": "Unintended acceleration",
    "fault_tree": {
      "top_event": {
        "id": "FT-TOP-H-001",
        "type": "top",
        "description": "Unintended acceleration",
        "gate_type": null
      },
      "events": [
        {
          "id": "FT-INT-H-001",
          "type": "intermediate",
          "description": "Any failure mode causing unintended acceleration",
          "gate_type": "OR"
        },
        {
          "id": "FT-FM-inverter-short",
          "type": "intermediate",
          "description": "Inverter short circuit",
          "gate_type": "OR"
        },
        {
          "id": "FT-BASIC-gate-driver-wear",
          "type": "basic",
          "description": "Gate driver component wear",
          "gate_type": null
        },
        {
          "id": "FT-BASIC-overvoltage",
          "type": "basic",
          "description": "Overvoltage stress",
          "gate_type": null
        }
      ],
      "relationships": [
        {"from": "FT-TOP-H-001", "to": "FT-INT-H-001", "type": "CAUSES"},
        {"from": "FT-INT-H-001", "to": "FT-FM-inverter-short", "type": "CAUSES"},
        {"from": "FT-FM-inverter-short", "to": "FT-BASIC-gate-driver-wear", "type": "CAUSES"},
        {"from": "FT-FM-inverter-short", "to": "FT-BASIC-overvoltage", "type": "CAUSES"}
      ]
    },
    "statistics": {
      "total_events": 4,
      "basic_events": 2,
      "intermediate_events": 1,
      "top_events": 1,
      "max_depth": 3
    },
    "warnings": [
      "No FMEA cause found for failure mode 'Sensor drift' - created basic event directly"
    ]
  }
}
```

### 5.4 Shortest Path

**Endpoint:** `GET /analytics/shortest-path?from=C-INV-001&to=H-001&max_length=6`

**Response:**
```json
{
  "status": "success",
  "data": {
    "from": {"id": "C-INV-001", "type": "Component", "name": "Inverter Controller"},
    "to": {"id": "H-001", "type": "Hazard", "description": "Unintended acceleration"},
    "paths": [
      {
        "length": 3,
        "nodes": [
          {"id": "C-INV-001", "type": "Component"},
          {"id": "FM-inverter-short", "type": "FailureMode"},
          {"id": "H-001", "type": "Hazard"}
        ],
        "relationships": [
          {"type": "HAS_FAILURE_MODE"},
          {"type": "CAN_LEAD_TO"}
        ]
      }
    ]
  }
}
```

---

## 6. Frontend Updates

### 6.1 New Pages

**Advanced Analytics Dashboard**
- Overview metrics:
  - Total components analyzed
  - Single points of failure count
  - High-centrality components count
- Weak Links table (sortable by weakness score, betweenness, etc.)
- Chart: Centrality distribution (histogram)
- Chart: Weakness score by component type

**Fault Tree Viewer**
- Hazard selector
- "Synthesize FT" button
- Tree visualization (hierarchical layout)
- Export FT as image or JSON
- Edit/refine FT (manual adjustments)
- Link to PFTA/SFTA for quantitative analysis (future)

### 6.2 Updated Components

**Component Detail Page (new or enhanced)**
- Component info
- Centrality metrics (with explanations)
- Weakness score and recommendations
- "Simulate removal" button → show impact
- Related hazards, defects, tests

**Graph Visualization (M2 enhancement)**
- Color nodes by weakness score (gradient: green → yellow → red)
- Size nodes by betweenness centrality
- Filter: "Show only high-centrality nodes"
- Highlight critical paths between selected nodes

---

## 7. Testing Strategy

### 7.1 Algorithm Validation

**Centrality Calculations:**
- Compare igraph results vs NetworkX (on same graph)
- Validate on known graphs with published centrality values
- Test edge cases: disconnected graph, single node, cycles

**FT Synthesis:**
- Create test hazards with known FT structures
- Synthesize FT and compare to hand-built FT
- Validate: no cycles, all basic events are leaves, correct gate logic

### 7.2 Performance Testing

- Benchmark centrality calculation on graphs of varying sizes (1K, 10K, 100K nodes)
- Ensure <10 second target for 10K nodes
- Profile memory usage

### 7.3 Integration Testing

- Calculate metrics, verify they're stored in Neo4j
- Query weak links endpoint, verify ranking is correct
- Synthesize FT, verify FTEvent nodes are created

---

## 8. Success Criteria

### 8.1 Functional

- [ ] Centrality metrics calculated for all Component nodes
- [ ] Weak links ranked correctly (vs manual expert analysis)
- [ ] Fault tree synthesized for test hazard matches hand-built FT structure
- [ ] Shortest path query returns correct path
- [ ] Frontend displays weak links dashboard

### 8.2 Performance

- [ ] Centrality calculation <10 seconds for 10K nodes
- [ ] FT synthesis <5 seconds for hazard with 50 failure modes
- [ ] Shortest path <500ms

### 8.3 Acceptance

**Demo Scenario:**
1. Calculate centrality metrics for full graph
2. Query weak links - identify top 5 components
3. Synthesize fault tree for hazard H-001
4. Visualize FT in frontend
5. Show component detail page with weakness score and recommendations
6. Export FT as image

**Acceptance Test:**
- Centrality-based weak link ranking matches expert judgment (>95% agreement on top 10)
- Synthesized FT covers >80% of hand-built FT structure
- Safety architect can identify critical components 10x faster than manual analysis

---

## 9. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Centrality metrics don't correlate with real criticality | High | Medium | Validate with experts, combine multiple metrics, allow manual overrides |
| FT synthesis produces invalid trees (cycles, wrong logic) | High | Medium | Extensive validation, conservative approach (use OR gates), allow manual editing |
| Performance degrades with large graphs | High | Medium | Use igraph (fast), optimize queries, provide async processing |
| Domain experts reject auto-generated FTs | Medium | High | Position as "starting point" not final FT, allow refinement, get early feedback |
| AND gate inference is inaccurate | Medium | High | Phase 4 v1: use only OR gates (conservative), defer AND gate inference to future |

---

## 10. Future Enhancements

### 10.1 Advanced FT Features

- Quantitative FTA (calculate top event probability)
- Integration with PFTA/SFTA libraries
- Import/export FT in standard formats (OpenFTA, etc.)
- Minimal cut sets calculation
- Common cause failure analysis

### 10.2 Machine Learning

- Learn AND gate patterns from historical FTs
- Predict component criticality using supervised learning
- Anomaly detection (unusual graph patterns)
- Automated ASIL recommendation based on graph structure

### 10.3 Simulation & Optimization

- What-if analysis: add/remove components, see impact on coverage and centrality
- Architecture optimization: suggest component placements to minimize weak links
- Redundancy analysis: identify where to add redundancy for maximum safety improvement

### 10.4 Community Detection

- Identify clusters/modules in safety architecture
- Detect coupling between subsystems
- Suggest architectural refactoring to reduce coupling

---

## 11. Appendix

### 11.1 Centrality Metrics Explained

**Betweenness Centrality:**
- Measures how often a node appears on shortest paths between other nodes
- High betweenness = "bridge" or "bottleneck"
- **Safety interpretation:** Component whose failure breaks many safety chains

**PageRank (Eigenvector Centrality):**
- Measures importance based on importance of neighbors
- High PageRank = connected to other important nodes
- **Safety interpretation:** Component in a critical cluster of safety-relevant nodes

**Degree Centrality:**
- Simply counts number of connections
- High degree = hub with many connections
- **Safety interpretation:** Component involved in many functions/relationships

**Closeness Centrality:**
- Measures average distance to all other nodes
- High closeness = can quickly affect many nodes
- **Safety interpretation:** Component whose changes ripple widely through system

### 11.2 Related Documents

- `prd-phase1.md` - Backend API specification
- `prd-phase2.md` - Frontend specification
- `prd-phase3.md` - Runtime Defects PRD
- `claude.md` - Project context

### 11.3 References

- Newman, M. E. J. (2010). *Networks: An Introduction*. Oxford University Press.
- Rausand, M., & Høyland, A. (2004). *System Reliability Theory: Models, Statistical Methods, and Applications*. Wiley.
- igraph documentation: https://igraph.org/python/
- Neo4j GDS documentation: https://neo4j.com/docs/graph-data-science/
- PFTA: https://pypi.org/project/pfta/
- SFTA: https://pypi.org/project/sfta/

---

**Document Status:** Draft
**Last Updated:** 2025-11-18
**Dependencies:** Phase 1, 2, 3 recommended but not strictly required
**Owner:** Advanced Analytics Team
