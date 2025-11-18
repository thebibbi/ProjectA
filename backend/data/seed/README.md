# Seed Data for Safety Graph Twin

This directory contains sample data for populating the Safety Graph Twin knowledge graph with a realistic EV traction inverter safety analysis.

## Overview

The seed data represents a complete safety analysis for an Electric Vehicle (EV) traction inverter system, including:

- **8 Hazards** from HARA analysis (ASIL A-D)
- **5 Operating Scenarios** (Highway, Urban, Regenerative Braking, Hill Climbing, Charging)
- **8 Safety Goals** addressing critical hazards
- **8 Components** (Hardware and Software)
- **8 Failure Modes** with FMEA analysis
- **8 FMEA Entries** with RPN calculations
- **12 Functional Safety Requirements** (FSRs)
- **17 Technical Safety Requirements** (TSRs)
- **20 Test Cases** with verification results
- **Complete traceability chains** from Hazard → SafetyGoal → FSR → TSR → TestCase

## Data Files

### hara_data.json

Contains HARA (Hazard Analysis and Risk Assessment) data:

**Hazards (8 total):**
- H-001: Unintended acceleration (ASIL D)
- H-002: Loss of regenerative braking (ASIL D)
- H-003: Motor torque oscillation (ASIL C)
- H-004: Inverter thermal runaway (ASIL D)
- H-005: High voltage isolation failure (ASIL D)
- H-006: Battery over-discharge (ASIL B)
- H-007: Motor speed sensor failure (ASIL A)
- H-008: DC link overvoltage (ASIL C)

**Operating Scenarios (5 total):**
- SC-HIGHWAY: High-speed highway operation
- SC-URBAN: Urban stop-and-go traffic
- SC-REGEN: Regenerative braking
- SC-CLIMB: Hill climbing with high torque
- SC-CHARGE: DC fast charging

**Safety Goals (8 total):**
- One safety goal per hazard with ASIL ratings, safe states, and fault tolerance times

**Relationships:**
- OCCURS_IN: Links hazards to operating scenarios
- MITIGATED_BY: Links hazards to safety goals

### fmea_data.json

Contains FMEA (Failure Mode and Effects Analysis) data:

**Components (8 total):**
- C-INV-001: Traction Inverter (Infineon HybridPACK-2)
- C-MCU-001: Motor Control Unit (NXP S32K344)
- C-GD-001: IGBT Gate Driver (TI UCC21750)
- C-RES-001: Resolver Interface (AD AD2S1210)
- C-DC-001: DC Link Capacitor Bank (TDK B32778G)
- C-COOL-001: Liquid Cooling System (Valeo TCS-300)
- C-SW-FOC: FOC Control Software (v2.3.1)
- C-SW-DIAG: Diagnostics Software (v1.5.2)

**Failure Modes (8 total):**
- FM-001: IGBT short circuit failure
- FM-002: Gate driver power supply failure
- FM-003: Resolver winding open circuit
- FM-004: DC link capacitor degradation
- FM-005: Coolant pump mechanical failure
- FM-006: MCU software corruption (bit flip)
- FM-007: Current sensor offset drift
- FM-008: Thermal interface material degradation

**FMEA Entries (8 total):**
- Complete FMEA analysis with:
  - Function description
  - Potential failure modes
  - Effects and causes
  - Current controls
  - Severity (1-10), Occurrence (1-10), Detection (1-10)
  - RPN = Severity × Occurrence × Detection
  - Recommended actions

**Relationships:**
- HAS_FAILURE_MODE: Links components to failure modes
- ANALYZED_IN: Links failure modes to FMEA entries

### requirements_data.json

Contains safety requirements with complete traceability:

**Functional Safety Requirements (12 FSRs):**
- FSR-010 to FSR-080: High-level functional requirements
- Derived from safety goals
- ASIL A-D ratings
- Status: approved

**Technical Safety Requirements (17 TSRs):**
- TSR-015 to TSR-086: Detailed technical implementations
- Refined from FSRs
- ASIL decomposition where applicable
- Verification methods specified (HIL, MIL, Vehicle, Lab testing)
- Allocated to specific components

**Relationships:**
- REFINED_TO: Links SafetyGoals → FSRs → TSRs (complete decomposition chain)
- ALLOCATED_TO: Links TSRs to implementing components

### tests_data.json

Contains test cases for verification:

**Test Cases (20 total):**
- TC-001 to TC-020: Comprehensive test suite
- Test types: HIL (Hardware-in-Loop), MIL (Model-in-Loop), Vehicle, Lab, Integration, Dyno
- Coverage levels: MC/DC, Branch, Statement
- All tests marked as PASSED with execution dates
- Pass criteria and actual results documented

**Test Coverage:**
- Torque command verification (TC-001, TC-002)
- Regenerative braking (TC-003, TC-004)
- FOC control (TC-005, TC-006)
- Thermal protection (TC-007, TC-008, TC-009)
- HV isolation (TC-010, TC-011)
- Battery management (TC-012, TC-013)
- Speed calculation (TC-014, TC-015)
- DC link protection (TC-016, TC-017)
- Component-level tests (TC-018, TC-019, TC-020)

**Relationships:**
- VERIFIED_BY: Links TSRs and Components to test cases

## Traceability Chains

The seed data provides complete traceability chains, for example:

**Example 1: Unintended Acceleration**
```
H-001 (Unintended acceleration)
  → SG-001 (Prevent unintended acceleration)
    → FSR-010 (Verify torque commands)
      → TSR-015 (Independent calculation channel)
        → TC-001 (Discrepancy detection test)
```

**Example 2: Thermal Protection**
```
H-004 (Inverter thermal runaway)
  → SG-004 (Prevent inverter thermal damage)
    → FSR-040 (Monitor temperature and limit power)
      → TSR-045 (Junction temperature estimation)
        → TC-007 (Thermal model validation)
```

## Usage

### Option 1: Using the Python Script (Recommended)

1. Ensure the API is running:
   ```bash
   cd backend
   poetry run uvicorn app.main:app --reload
   ```

2. Load all seed data:
   ```bash
   poetry run python scripts/load_seed_data.py
   ```

3. Or specify a different API URL:
   ```bash
   poetry run python scripts/load_seed_data.py --api-url http://localhost:8000
   ```

The script will:
- Check API health
- Import data in correct dependency order (HARA → FMEA → Requirements → Tests)
- Report statistics on success
- Exit with code 0 on success, 1 on failure

### Option 2: Manual Import via API

Import each file individually using curl or Postman:

```bash
# 1. Import HARA data
curl -X POST http://localhost:8000/import/hara \
  -H "Content-Type: application/json" \
  -d @data/seed/hara_data.json

# 2. Import FMEA data
curl -X POST http://localhost:8000/import/fmea \
  -H "Content-Type: application/json" \
  -d @data/seed/fmea_data.json

# 3. Import Requirements
curl -X POST http://localhost:8000/import/requirements \
  -H "Content-Type: application/json" \
  -d @data/seed/requirements_data.json

# 4. Import Tests
curl -X POST http://localhost:8000/import/tests \
  -H "Content-Type: application/json" \
  -d @data/seed/tests_data.json
```

### Option 3: Using the OpenAPI UI

1. Navigate to http://localhost:8000/docs
2. Use the `/import/hara`, `/import/fmea`, `/import/requirements`, and `/import/tests` endpoints
3. Copy-paste JSON content from each file
4. Execute imports in order

## Verification

After loading the seed data, verify the import:

### 1. Check Statistics

```bash
curl http://localhost:8000/analytics/statistics
```

Expected output:
- Total nodes: ~80+
- Total relationships: ~100+
- Hazards: 8
- Verified hazards: 8
- Coverage: 100%

### 2. Check Hazard Coverage

```bash
curl http://localhost:8000/analytics/coverage/hazards
```

Should show all 8 hazards with "full" coverage status.

### 3. Check Component Impact

```bash
curl http://localhost:8000/analytics/impact/components
```

Should show all components ranked by impact score.

### 4. Query Specific Hazard

```bash
curl http://localhost:8000/analytics/coverage/hazard/H-001
```

Should show complete traceability chain for H-001.

### 5. Get Traceability Chain

```bash
curl http://localhost:8000/analytics/traceability/hazard/H-001
```

Should show full path: H-001 → SG-001 → FSR-010/FSR-011 → TSR-015/TSR-016 → TC-001/TC-002

## Data Quality

All seed data follows ISO 26262 best practices:

- **ASIL ratings** are consistent across decomposition chains
- **RPN values** are calculated correctly (S × O × D)
- **Test coverage** includes all critical requirements
- **Traceability** is bidirectional and complete
- **Component allocations** are realistic for automotive systems
- **Verification methods** are appropriate for ASIL levels
- **Timing requirements** are realistic for safety-critical systems

## Extending the Data

To add more seed data:

1. Follow the JSON structure in existing files
2. Ensure ID patterns match (e.g., H-*, FSR-*, TC-*)
3. Maintain ASIL consistency in traceability chains
4. Add relationships to link new entities
5. Update this README with new content

## Real-World Applicability

This seed data is based on real EV traction inverter safety analyses and can be used as a template for:

- **Training**: Learning ISO 26262 and functional safety concepts
- **Demonstrations**: Showing knowledge graph capabilities
- **Testing**: Validating safety graph twin functionality
- **Templates**: Starting point for actual projects

## Notes

- All test cases are marked as "passed" for demonstration purposes
- Actual production systems would have more granular requirements and tests
- RPN thresholds and recommended actions follow automotive industry standards
- Component part numbers are real products from major suppliers
- Timing requirements (fault tolerance times, detection latencies) are realistic for ASIL D systems

---

**Last Updated**: 2025-11-18
**Version**: 1.0 (M1.9)
