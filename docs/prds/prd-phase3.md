# Product Requirements Document: Phase 3 - Runtime Defects Integration

**Project:** Safety Graph Twin
**Phase:** M3 - Runtime Defects Integration ("Closed Loop Safety Graph")
**Version:** 1.0
**Date:** 2025-11-18
**Status:** Planning
**Dependencies:** Phase 1 (Core KG & ETL), Phase 2 (Frontend) should be complete

---

## 1. Executive Summary

### 1.1 Overview

Phase 3 closes the loop between design-time safety analysis and runtime field data by integrating defect instances, warranty claims, and field events into the Safety Graph Twin. This enables the critical capability of comparing predicted risks (from HARA/FMEA) against observed real-world failures, identifying underestimated hazards and validating safety analyses.

### 1.2 Business Value

**Key Capabilities:**
- **Validate Safety Analyses:** Compare predicted failure rates vs actual defect data
- **Identify Blind Spots:** Find hazards with low ASIL but high real-world defect counts
- **Continuous Improvement:** Feed field data back into next design iteration
- **Compliance Evidence:** Demonstrate continuous monitoring per ISO 26262 Part 8

**ROI:**
- Reduce warranty costs by identifying systematic issues early
- Improve ASIL assignments based on real-world data
- Accelerate root cause analysis (link defect → component → hazard in seconds)

### 1.3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Defect Import Speed | <5 seconds for 1000 defects | Benchmark |
| Discrepancy Detection Accuracy | 100% (vs manual analysis) | Validation testing |
| Root Cause Trace Time | <30 seconds (defect → hazard chain) | User testing |
| Predictive Accuracy Improvement | >20% for next design cycle | Historical comparison |

---

## 2. Problem Statement

### 2.1 Current Pain Points

**For Safety Engineers:**
- Field defect data lives in separate systems (warranty DB, service reports, Jira)
- No automated way to link defects back to safety analyses (FMEA, HARA)
- Difficult to determine if a defect invalidates ASIL assignment
- Cannot easily identify which hazards are underestimated

**For Reliability Engineers:**
- Performing root cause analysis requires manually tracing through documentation
- No visibility into which defects are safety-relevant vs quality issues
- Cannot prioritize fixes based on safety impact

**For Program Managers:**
- No dashboard showing "predicted vs actual" risk
- Cannot demonstrate continuous improvement for audits
- Reactive rather than proactive issue management

### 2.2 User Stories

**US1:** As a safety engineer, I want to import field defect data and automatically link it to components and failure modes, so I can validate my FMEA analysis.

**US2:** As a safety engineer, I want to see which hazards have more defects than predicted, so I can update ASIL assignments for the next design iteration.

**US3:** As a reliability engineer, I want to trace a defect back to its related hazards and safety goals, so I can assess safety impact during root cause analysis.

**US4:** As a program manager, I want a dashboard showing predicted vs observed risk by hazard, so I can demonstrate continuous improvement to auditors.

---

## 3. Requirements

### 3.1 Functional Requirements

#### FR1: Defect Data Model

**FR1.1 DefectInstance Node**
- MUST support properties:
  - `id` (string, unique): Defect identifier (e.g., from warranty system)
  - `timestamp` (datetime): When defect occurred
  - `severity` (string): Critical, Major, Minor (can be different from ASIL)
  - `description` (string): Defect description
  - `status` (string): Open, In Progress, Resolved, Closed
  - `source` (string): Where defect came from (warranty, field, CV, test)
  - `vehicle_id` (string, optional): VIN or vehicle identifier
  - `mileage` (number, optional): Mileage when defect occurred
  - `environmental_conditions` (string, optional): Temperature, weather, etc.
- SHOULD support custom properties for domain-specific data

**FR1.2 Defect Relationships**
- MUST support: `(DefectInstance)-[:OBSERVED_AT]->(Component)`
- MUST support: `(DefectInstance)-[:INSTANCE_OF]->(FailureMode)`
- SHOULD support: `(DefectInstance)-[:RELATED_TO]->(Hazard)` (derived or explicit)
- SHOULD support: `(DefectInstance)-[:SIMILAR_TO]->(DefectInstance)` (for clustering)

#### FR2: Defect Import

**FR2.1 Import Endpoint**
- MUST provide `POST /import/defects` endpoint
- MUST accept JSON payload with defects and linkages:
  ```json
  {
    "defects": [
      {
        "id": "D-00123",
        "timestamp": "2025-10-15T14:30:00Z",
        "severity": "Critical",
        "description": "Inverter gate driver short circuit",
        "status": "Open",
        "source": "warranty",
        "component_id": "C-INV-GD-001",
        "failure_mode": "Gate driver short circuit"
      }
    ]
  }
  ```
- MUST validate defect data (required fields, valid timestamps, etc.)
- MUST create or link to existing FailureMode nodes
- MUST link DefectInstance to Component
- SHOULD infer RELATED_TO Hazard relationship based on Component → FailureMode → Hazard path

**FR2.2 CSV Import Support**
- SHOULD support CSV file upload
- CSV columns: defect_id, timestamp, severity, description, status, source, component_id, failure_mode
- SHOULD handle missing or partial data gracefully

**FR2.3 Batch Import**
- MUST support importing >1000 defects in single request
- MUST process in batches with transaction rollback on error
- SHOULD provide import progress for large datasets

#### FR3: Discrepancy Analysis

**FR3.1 Predicted vs Observed Risk**
- MUST calculate defect frequency per hazard:
  - Count DefectInstance nodes linked to each Hazard
  - Normalize by time period (defects per month/year)
- MUST compare observed frequency vs predicted exposure/occurrence:
  - HARA exposure rating (E0-E4)
  - FMEA occurrence rating (1-10)
- MUST identify discrepancies:
  - **Underestimated Hazards:** High defect count but low ASIL (e.g., ASIL-A with 50 defects)
  - **Overestimated Hazards:** Low/no defects but high ASIL (validation of safety measures)
  - **Unknown Hazards:** Defects with no linked hazard (gaps in HARA)

**FR3.2 Component Risk Heatmap**
- MUST identify components with disproportionate defect counts
- MUST rank components by:
  - Total defects
  - Critical defects
  - Safety-relevant defects (linked to ASIL-C/D hazards)
- SHOULD support filtering by time range, defect source, severity

**FR3.3 Discrepancy Endpoint**
- MUST provide `GET /analytics/discrepancy` endpoint
- MUST return:
  - List of underestimated hazards (with defect count, predicted ASIL, recommended ASIL)
  - List of high-defect components
  - List of defects with no hazard linkage
- SHOULD support filtering by ASIL, time range, defect severity

#### FR4: Defect Trace Analysis

**FR4.1 Root Cause Trace**
- MUST provide `GET /analytics/defect-trace/{defect_id}` endpoint
- MUST return full trace:
  - DefectInstance → Component → FailureMode → Hazard → SafetyGoal → Requirements → Tests
- MUST identify:
  - Which safety goal is impacted
  - Which requirements are affected
  - Whether related tests exist and their status
- SHOULD identify similar defects (same failure mode, component, or pattern)

**FR4.2 Defect Clustering**
- SHOULD group similar defects by:
  - Same failure mode
  - Same component
  - Same hazard
  - Time proximity (defect bursts)
- SHOULD provide `GET /analytics/defect-clusters` endpoint

#### FR5: Time-Series Analysis (Optional)

**FR5.1 Defect Trends**
- SHOULD provide `GET /analytics/defect-trends` endpoint
- SHOULD return defect counts over time:
  - By hazard
  - By component
  - By failure mode
  - By severity
- SHOULD support configurable time buckets (daily, weekly, monthly)

**FR5.2 Leading Indicators**
- SHOULD identify patterns:
  - Increasing defect rate for specific hazard
  - Seasonal variations
  - Correlation with mileage/usage

### 3.2 Non-Functional Requirements

**NFR1: Performance**
- Import 1000 defects in <5 seconds
- Discrepancy analysis completes in <2 seconds
- Defect trace analysis completes in <1 second

**NFR2: Data Quality**
- MUST handle incomplete defect data (missing component ID, failure mode)
- MUST flag defects that cannot be linked to KG entities
- SHOULD provide data quality metrics (% linked, % with hazard trace)

**NFR3: Privacy**
- MUST NOT store PII (VINs can be pseudonymized)
- MUST support data anonymization for sharing
- SHOULD support data retention policies (delete defects after N years)

---

## 4. Technical Design

### 4.1 Extended Graph Schema

**New Node:**
```cypher
(:DefectInstance {
  id: string,
  timestamp: datetime,
  severity: string,
  description: string,
  status: string,
  source: string,
  vehicle_id: string,  // optional, pseudonymized
  mileage: integer,    // optional
  environmental_conditions: string  // optional
})
```

**New Relationships:**
```cypher
(DefectInstance)-[:OBSERVED_AT]->(Component)
(DefectInstance)-[:INSTANCE_OF]->(FailureMode)
(DefectInstance)-[:RELATED_TO]->(Hazard)  // inferred or explicit
```

### 4.2 Discrepancy Analysis Algorithm

**Pseudocode:**
```python
def analyze_discrepancy():
    for hazard in all_hazards:
        # Count defects linked to this hazard
        defect_count = count_defects_for_hazard(hazard.id)

        # Get predicted exposure/occurrence
        predicted_asil = hazard.asil
        predicted_exposure = hazard.exposure  # E0-E4

        # Calculate observed frequency (defects per year)
        time_range = get_time_range()  # e.g., last 2 years
        observed_frequency = defect_count / time_range.years

        # Determine discrepancy
        if predicted_asil in ['QM', 'A'] and observed_frequency > threshold_high:
            # Underestimated hazard
            yield {
                'hazard_id': hazard.id,
                'status': 'underestimated',
                'defect_count': defect_count,
                'predicted_asil': predicted_asil,
                'recommended_asil': calculate_recommended_asil(observed_frequency),
                'reason': f'{defect_count} defects observed but ASIL {predicted_asil}'
            }
        elif predicted_asil in ['C', 'D'] and observed_frequency < threshold_low:
            # Overestimated or well-mitigated
            yield {
                'hazard_id': hazard.id,
                'status': 'well_mitigated',
                'defect_count': defect_count,
                'predicted_asil': predicted_asil,
                'reason': f'High ASIL but only {defect_count} defects (safety measures effective)'
            }
```

**Cypher Query Example:**
```cypher
// Find underestimated hazards
MATCH (h:Hazard)<-[:RELATED_TO]-(d:DefectInstance)
WHERE h.asil IN ['QM', 'A']
WITH h, count(d) as defect_count
WHERE defect_count > 10  // threshold
RETURN h.id, h.description, h.asil, defect_count,
       'B' as recommended_asil  // simplified, could be calculated
ORDER BY defect_count DESC
```

### 4.3 Defect Trace Query

```cypher
// Trace defect to hazard and safety artifacts
MATCH path = (d:DefectInstance {id: $defect_id})
  -[:OBSERVED_AT]->(c:Component)
  -[:REALIZED_BY*0..2]-(f:Function)
  <-[:FOR_FUNCTION]-(fmea:FMEAEntry)
  -[:HAS_FAILURE_MODE]->(fm:FailureMode)
  -[:CAN_LEAD_TO]->(h:Hazard)
  -[:MITIGATED_BY]->(sg:SafetyGoal)
  -[:REFINED_INTO]->(req:FunctionalSafetyRequirement)
  -[:VERIFIED_BY]->(tc:TestCase)
RETURN d, c, f, fmea, fm, h, sg, req, tc, path
```

---

## 5. API Specification

### 5.1 Import Defects

**Endpoint:** `POST /import/defects`

**Request:**
```json
{
  "defects": [
    {
      "id": "D-00123",
      "timestamp": "2025-10-15T14:30:00Z",
      "severity": "Critical",
      "description": "Inverter gate driver short circuit during acceleration",
      "status": "Open",
      "source": "warranty",
      "component_id": "C-INV-GD-001",
      "failure_mode": "Gate driver short circuit",
      "vehicle_id": "VIN-XXXX1234",  // pseudonymized
      "mileage": 45000,
      "environmental_conditions": "Temperature: 35°C, Highway"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "defects_created": 1,
    "components_linked": 1,
    "failure_modes_created": 0,  // already existed
    "failure_modes_linked": 1,
    "hazards_inferred": 1,
    "defects_without_component": 0,
    "defects_without_failure_mode": 0
  },
  "warnings": [
    "Defect D-00124 has no matching component_id 'C-UNKNOWN'"
  ]
}
```

### 5.2 Discrepancy Analysis

**Endpoint:** `GET /analytics/discrepancy?time_range=2y&min_defects=5`

**Response:**
```json
{
  "status": "success",
  "data": {
    "underestimated_hazards": [
      {
        "hazard_id": "H-015",
        "description": "Battery thermal runaway",
        "predicted_asil": "A",
        "defect_count": 47,
        "defects_per_year": 23.5,
        "recommended_asil": "C",
        "reason": "47 defects observed over 2 years but ASIL A",
        "sample_defects": ["D-00123", "D-00145", "D-00167"]
      }
    ],
    "well_mitigated_hazards": [
      {
        "hazard_id": "H-001",
        "description": "Unintended acceleration",
        "predicted_asil": "D",
        "defect_count": 2,
        "defects_per_year": 1.0,
        "reason": "High ASIL but only 2 defects (safety measures effective)"
      }
    ],
    "unknown_hazards": [
      {
        "defect_ids": ["D-00234", "D-00235"],
        "failure_mode": "CAN bus corruption",
        "component": "C-CAN-001",
        "defect_count": 12,
        "reason": "No linked hazard in HARA (gap in safety analysis)"
      }
    ],
    "high_defect_components": [
      {
        "component_id": "C-INV-GD-001",
        "component_name": "Inverter Gate Driver",
        "defect_count": 89,
        "critical_defects": 23,
        "safety_relevant_defects": 47,
        "top_failure_modes": [
          {"name": "Short circuit", "count": 45},
          {"name": "Overheating", "count": 30}
        ]
      }
    ]
  },
  "meta": {
    "time_range": "2023-11-18 to 2025-11-18",
    "total_defects_analyzed": 1234,
    "timestamp": "2025-11-18T10:30:00Z"
  }
}
```

### 5.3 Defect Trace

**Endpoint:** `GET /analytics/defect-trace/D-00123`

**Response:**
```json
{
  "status": "success",
  "data": {
    "defect": {
      "id": "D-00123",
      "description": "Inverter gate driver short circuit",
      "timestamp": "2025-10-15T14:30:00Z",
      "severity": "Critical"
    },
    "trace": {
      "component": {
        "id": "C-INV-GD-001",
        "name": "Inverter Gate Driver",
        "type": "hardware"
      },
      "failure_mode": {
        "name": "Gate driver short circuit",
        "category": "electrical"
      },
      "hazards": [
        {
          "id": "H-001",
          "description": "Unintended acceleration",
          "asil": "D"
        }
      ],
      "safety_goals": [
        {
          "id": "SG-001",
          "description": "Prevent unintended acceleration >2 m/s²",
          "asil": "D"
        }
      ],
      "requirements": [
        {
          "id": "FSR-010",
          "text": "Detect inverter failure within 100ms",
          "asil": "D"
        }
      ],
      "tests": [
        {
          "id": "TC-045",
          "name": "Inverter fault injection test",
          "status": "passed"
        }
      ]
    },
    "similar_defects": [
      {"id": "D-00145", "timestamp": "2025-10-20T09:15:00Z"},
      {"id": "D-00167", "timestamp": "2025-10-25T16:45:00Z"}
    ],
    "analysis": {
      "safety_impact": "Critical - linked to ASIL-D hazard",
      "test_coverage": "Test TC-045 passed but defect still occurred - investigate test adequacy",
      "recommendation": "Review FSR-010 requirement and update test scenario"
    }
  }
}
```

---

## 6. Frontend Updates

### 6.1 New Pages

**Defects Dashboard**
- List of recent defects (table)
- Filters: severity, status, time range, component, failure mode
- Click defect to see trace
- Export to CSV

**Discrepancy Dashboard**
- Overview metrics:
  - Total defects analyzed
  - Underestimated hazards count
  - Well-mitigated hazards count
  - Unknown hazards count
- Underestimated Hazards table (sortable)
- High-Defect Components chart (bar chart)
- Time-series chart: defects over time by hazard

**Defect Detail Page**
- Defect details
- Full trace visualization (graph or tree)
- Similar defects
- Analysis and recommendations
- Actions: Link to additional hazard, update status, export report

### 6.2 Updated Components

**Dashboard (M2)**
- Add "Recent Defects" widget
- Add "Top At-Risk Components" widget

**Impact Explorer (M2)**
- Show defect count badge on components
- Filter to show only components with defects

**Graph Visualization (M2)**
- Add DefectInstance as node type (color: red/orange)
- Show defect count on component nodes
- Filter: "Show only safety-relevant defects"

---

## 7. Data Integration Strategy

### 7.1 Data Sources

**Common Sources:**
- Warranty Management System (WMS)
- Service Ticketing System (JIRA, ServiceNow)
- Vehicle Telemetry / Connected Vehicle Platform
- Field Test Reports
- Customer Complaints Database

### 7.2 ETL Pipeline (Future)

**Phase 3 v1:** Manual CSV import
**Phase 3 v2 (future):** Automated ETL
- Scheduled import from WMS API (daily/weekly)
- Real-time ingestion via message queue (Kafka, RabbitMQ)
- Data transformation layer (map WMS fields to DefectInstance schema)

### 7.3 Data Mapping

**Example Mapping:**
| Source Field (WMS) | Target Field (DefectInstance) | Transformation |
|-------------------|------------------------------|----------------|
| warranty_claim_id | id | Prefix with "D-" |
| reported_date | timestamp | Convert to ISO 8601 |
| failure_description | description | Truncate to 500 chars |
| component_part_number | component_id | Lookup in Component table |
| failure_code | failure_mode | Map failure code to failure mode name |

### 7.4 Data Quality Challenges

**Challenge:** Defect data may not have clean component IDs or failure modes
**Solution:**
- Use fuzzy matching on component names
- Provide UI to manually link unmatched defects
- Flag defects without links for review

**Challenge:** Defect severity may not map directly to ASIL
**Solution:**
- Maintain separate severity field
- Infer safety relevance based on linked hazard ASIL

---

## 8. Testing Strategy

### 8.1 Unit Tests

- Test defect import with valid/invalid data
- Test discrepancy calculation logic
- Test defect trace query with various paths

### 8.2 Integration Tests

- Import defects, verify linkages to components/failure modes
- Run discrepancy analysis, verify underestimated hazards detected
- Test defect trace for complete path

### 8.3 Data Validation Tests

- Import defects with missing component IDs - verify graceful handling
- Import duplicate defects - verify deduplication or error
- Import defects with future timestamps - verify validation error

---

## 9. Success Criteria

### 9.1 Functional

- [ ] Import 100 defects from CSV
- [ ] Defects correctly linked to components and failure modes
- [ ] Discrepancy analysis identifies known underestimated hazard (from test data)
- [ ] Defect trace returns complete path to hazard and requirements
- [ ] Frontend displays discrepancy dashboard with correct data

### 9.2 Performance

- [ ] Import 1000 defects in <5 seconds
- [ ] Discrepancy analysis completes in <2 seconds
- [ ] Defect trace completes in <1 second

### 9.3 Acceptance

**Demo Scenario:**
1. Import 50 real-world defects (anonymized)
2. Run discrepancy analysis
3. Identify 1-2 hazards with high defect count but low ASIL
4. Trace specific defect to hazard and safety goal
5. Show frontend dashboard with underestimated hazards
6. Export discrepancy report

---

## 10. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Defect data quality is poor (missing IDs) | High | High | Fuzzy matching, manual review UI, data quality metrics |
| Cannot establish clear component/failure mode linkage | High | Medium | Provide manual linking UI, use text similarity for suggestions |
| Discrepancy thresholds are arbitrary | Medium | High | Make thresholds configurable, provide statistical analysis tools |
| Privacy concerns with VINs/PII | High | Medium | Pseudonymize data, provide anonymization utilities, document policy |
| Performance degrades with millions of defects | Medium | Medium | Implement time-based partitioning, archive old defects |

---

## 11. Future Enhancements

- Real-time defect ingestion (Kafka integration)
- Machine learning for defect clustering and pattern detection
- Predictive models: predict which components will fail next
- Automated ASIL reassignment recommendations
- Integration with field update/recall systems
- Defect cost analysis (warranty cost per hazard)

---

## 12. Appendix

### 12.1 Related Documents

- `prd-phase1.md` - Backend API specification
- `prd-phase2.md` - Frontend specification
- `prd-phase4.md` - Advanced Analytics PRD
- `claude.md` - Project context

### 12.2 References

- ISO 26262-8:2018 - Supporting processes (continuous improvement)
- ISO 26262-10:2018 - Guideline on ISO 26262

---

**Document Status:** Draft
**Last Updated:** 2025-11-18
**Dependencies:** Phase 1 and 2 should be complete
**Owner:** Safety Engineering Team
