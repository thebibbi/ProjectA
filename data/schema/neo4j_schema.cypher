// ============================================================================
// Safety Graph Twin - Neo4j Schema Definition
// ============================================================================
// Version: 1.0
// Purpose: Define constraints, indexes, and schema for ISO 26262 + STPA
//          knowledge graph
// Note: STPA nodes included for Phase 5 compatibility (hybrid approach)
// ============================================================================

// ============================================================================
// PART 1: UNIQUENESS CONSTRAINTS
// ============================================================================
// Ensures each node type has unique IDs

// Architecture Nodes
CREATE CONSTRAINT item_id_unique IF NOT EXISTS
FOR (n:Item) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT function_id_unique IF NOT EXISTS
FOR (n:Function) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT component_id_unique IF NOT EXISTS
FOR (n:Component) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT signal_id_unique IF NOT EXISTS
FOR (n:Signal) REQUIRE n.id IS UNIQUE;

// Safety Nodes
CREATE CONSTRAINT hazard_id_unique IF NOT EXISTS
FOR (n:Hazard) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT scenario_id_unique IF NOT EXISTS
FOR (n:Scenario) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT safety_goal_id_unique IF NOT EXISTS
FOR (n:SafetyGoal) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT fsr_id_unique IF NOT EXISTS
FOR (n:FunctionalSafetyRequirement) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT tsr_id_unique IF NOT EXISTS
FOR (n:TechnicalSafetyRequirement) REQUIRE n.id IS UNIQUE;

// Analysis Nodes
CREATE CONSTRAINT fmea_entry_id_unique IF NOT EXISTS
FOR (n:FMEAEntry) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT failure_mode_name_unique IF NOT EXISTS
FOR (n:FailureMode) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT ft_event_id_unique IF NOT EXISTS
FOR (n:FTEvent) REQUIRE n.id IS UNIQUE;

// Verification Nodes
CREATE CONSTRAINT test_case_id_unique IF NOT EXISTS
FOR (n:TestCase) REQUIRE n.id IS UNIQUE;

// Runtime Nodes (Phase 3)
CREATE CONSTRAINT defect_instance_id_unique IF NOT EXISTS
FOR (n:DefectInstance) REQUIRE n.id IS UNIQUE;

// STPA Nodes (Phase 5 - placeholders)
CREATE CONSTRAINT uca_id_unique IF NOT EXISTS
FOR (n:UnsafeControlAction) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT control_structure_id_unique IF NOT EXISTS
FOR (n:ControlStructure) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT loss_scenario_id_unique IF NOT EXISTS
FOR (n:LossScenario) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT safety_constraint_id_unique IF NOT EXISTS
FOR (n:SafetyConstraint) REQUIRE n.id IS UNIQUE;

// Compliance Nodes (Optional)
CREATE CONSTRAINT standard_clause_id_unique IF NOT EXISTS
FOR (n:StandardClause) REQUIRE n.id IS UNIQUE;

// ============================================================================
// PART 2: PROPERTY EXISTENCE CONSTRAINTS
// ============================================================================
// Ensures critical properties always exist

// Architecture - required properties
CREATE CONSTRAINT item_name_exists IF NOT EXISTS
FOR (n:Item) REQUIRE n.name IS NOT NULL;

CREATE CONSTRAINT component_name_exists IF NOT EXISTS
FOR (n:Component) REQUIRE n.name IS NOT NULL;

CREATE CONSTRAINT function_name_exists IF NOT EXISTS
FOR (n:Function) REQUIRE n.name IS NOT NULL;

CREATE CONSTRAINT signal_name_exists IF NOT EXISTS
FOR (n:Signal) REQUIRE n.name IS NOT NULL;

// Safety - required properties
CREATE CONSTRAINT hazard_description_exists IF NOT EXISTS
FOR (n:Hazard) REQUIRE n.description IS NOT NULL;

CREATE CONSTRAINT hazard_asil_exists IF NOT EXISTS
FOR (n:Hazard) REQUIRE n.asil IS NOT NULL;

CREATE CONSTRAINT safety_goal_description_exists IF NOT EXISTS
FOR (n:SafetyGoal) REQUIRE n.description IS NOT NULL;

CREATE CONSTRAINT safety_goal_asil_exists IF NOT EXISTS
FOR (n:SafetyGoal) REQUIRE n.asil IS NOT NULL;

CREATE CONSTRAINT fsr_text_exists IF NOT EXISTS
FOR (n:FunctionalSafetyRequirement) REQUIRE n.text IS NOT NULL;

// Verification - required properties
CREATE CONSTRAINT test_case_name_exists IF NOT EXISTS
FOR (n:TestCase) REQUIRE n.name IS NOT NULL;

CREATE CONSTRAINT test_case_status_exists IF NOT EXISTS
FOR (n:TestCase) REQUIRE n.status IS NOT NULL;

// ============================================================================
// PART 3: INDEXES FOR PERFORMANCE
// ============================================================================
// Create indexes on frequently queried properties

// ASIL-based queries (very common)
CREATE INDEX hazard_asil_idx IF NOT EXISTS
FOR (n:Hazard) ON (n.asil);

CREATE INDEX safety_goal_asil_idx IF NOT EXISTS
FOR (n:SafetyGoal) ON (n.asil);

CREATE INDEX fsr_asil_idx IF NOT EXISTS
FOR (n:FunctionalSafetyRequirement) ON (n.asil);

// Name-based searches
CREATE INDEX item_name_idx IF NOT EXISTS
FOR (n:Item) ON (n.name);

CREATE INDEX component_name_idx IF NOT EXISTS
FOR (n:Component) ON (n.name);

CREATE INDEX function_name_idx IF NOT EXISTS
FOR (n:Function) ON (n.name);

CREATE INDEX signal_name_idx IF NOT EXISTS
FOR (n:Signal) ON (n.name);

// Status-based queries
CREATE INDEX test_case_status_idx IF NOT EXISTS
FOR (n:TestCase) ON (n.status);

CREATE INDEX defect_instance_status_idx IF NOT EXISTS
FOR (n:DefectInstance) ON (n.status);

// Type-based filtering
CREATE INDEX component_type_idx IF NOT EXISTS
FOR (n:Component) ON (n.type);

CREATE INDEX ft_event_type_idx IF NOT EXISTS
FOR (n:FTEvent) ON (n.type);

// Timestamp-based queries (for defects and temporal analysis)
CREATE INDEX defect_instance_timestamp_idx IF NOT EXISTS
FOR (n:DefectInstance) ON (n.timestamp);

// Severity-based queries
CREATE INDEX defect_instance_severity_idx IF NOT EXISTS
FOR (n:DefectInstance) ON (n.severity);

CREATE INDEX fmea_entry_rpn_idx IF NOT EXISTS
FOR (n:FMEAEntry) ON (n.rpn);

// ============================================================================
// PART 4: COMPOSITE INDEXES (for complex queries)
// ============================================================================
// Indexes on multiple properties for common query patterns

// Hazard filtering by ASIL + coverage status
CREATE INDEX hazard_asil_coverage_idx IF NOT EXISTS
FOR (n:Hazard) ON (n.asil, n.coverage_status);

// Test case filtering by status + type
CREATE INDEX test_case_status_type_idx IF NOT EXISTS
FOR (n:TestCase) ON (n.status, n.test_type);

// Component filtering by type + criticality
CREATE INDEX component_type_criticality_idx IF NOT EXISTS
FOR (n:Component) ON (n.type, n.is_critical);

// ============================================================================
// PART 5: FULL-TEXT SEARCH INDEXES
// ============================================================================
// Enable text search on descriptions

CREATE FULLTEXT INDEX hazard_description_fulltext IF NOT EXISTS
FOR (n:Hazard) ON EACH [n.description];

CREATE FULLTEXT INDEX safety_goal_description_fulltext IF NOT EXISTS
FOR (n:SafetyGoal) ON EACH [n.description];

CREATE FULLTEXT INDEX fmea_entry_fulltext IF NOT EXISTS
FOR (n:FMEAEntry) ON EACH [n.failure_mode, n.effect, n.cause];

CREATE FULLTEXT INDEX test_case_fulltext IF NOT EXISTS
FOR (n:TestCase) ON EACH [n.name, n.description];

// ============================================================================
// SCHEMA DOCUMENTATION
// ============================================================================
// The following node types and properties are defined in the schema:
//
// ARCHITECTURE NODES:
// -------------------
// Item {id, name, description, type}
// Function {id, name, description}
// Component {id, name, type, version, is_critical}
// Signal {id, name, unit, datatype}
//
// SAFETY NODES:
// -------------
// Hazard {id, description, asil, severity, exposure, controllability, coverage_status}
// Scenario {id, name, description}
// SafetyGoal {id, description, asil}
// FunctionalSafetyRequirement {id, text, asil}
// TechnicalSafetyRequirement {id, text, asil_decomposition}
//
// ANALYSIS NODES:
// ---------------
// FMEAEntry {id, failure_mode, effect, cause, detection, rpn, severity, occurrence}
// FailureMode {name, description, category}
// FTEvent {id, type, description, gate_type}
//
// VERIFICATION NODES:
// -------------------
// TestCase {id, name, status, test_type, coverage_level, description}
//
// RUNTIME NODES (Phase 3):
// -------------------------
// DefectInstance {id, timestamp, severity, description, status, source, vehicle_id, mileage}
//
// STPA NODES (Phase 5):
// ---------------------
// UnsafeControlAction {id, description, control_action, context, hazard_link}
// ControlStructure {id, name, controller_type, controlled_process}
// LossScenario {id, description, causal_factors}
// SafetyConstraint {id, text, relates_to_uca}
//
// COMPLIANCE NODES:
// -----------------
// StandardClause {id, standard, clause_number, title, text}
//
// ============================================================================
// RELATIONSHIP TYPES:
// ============================================================================
//
// Architecture relationships:
//   (Item)-[:HAS_FUNCTION]->(Function)
//   (Function)-[:REALIZED_BY]->(Component)
//   (Function)-[:USES_SIGNAL]->(Signal)
//   (Component)-[:CONNECTED_TO]->(Component)
//
// Safety concept relationships:
//   (Hazard)-[:IN_SCENARIO]->(Scenario)
//   (Hazard)-[:MITIGATED_BY]->(SafetyGoal)
//   (SafetyGoal)-[:REFINED_INTO]->(FunctionalSafetyRequirement)
//   (FunctionalSafetyRequirement)-[:REFINED_INTO]->(TechnicalSafetyRequirement)
//   (FunctionalSafetyRequirement)-[:ALLOCATED_TO]->(Item|Function|Component)
//   (TechnicalSafetyRequirement)-[:ALLOCATED_TO]->(Component)
//
// Analysis relationships:
//   (FMEAEntry)-[:FOR_FUNCTION]->(Function)
//   (FMEAEntry)-[:HAS_FAILURE_MODE]->(FailureMode)
//   (FailureMode)-[:CAN_LEAD_TO]->(Hazard)
//   (FTEvent)-[:CAUSES]->(FTEvent)
//   (FTEvent)-[:ASSOCIATED_WITH]->(FailureMode|Component)
//
// Verification relationships:
//   (FunctionalSafetyRequirement)-[:VERIFIED_BY]->(TestCase)
//   (TechnicalSafetyRequirement)-[:VERIFIED_BY]->(TestCase)
//   (TestCase)-[:COVERS_SIGNAL]->(Signal)
//   (TestCase)-[:COVERS_COMPONENT]->(Component)
//
// Runtime relationships (Phase 3):
//   (DefectInstance)-[:OBSERVED_AT]->(Component)
//   (DefectInstance)-[:INSTANCE_OF]->(FailureMode)
//   (DefectInstance)-[:RELATED_TO]->(Hazard)
//
// STPA relationships (Phase 5):
//   (UnsafeControlAction)-[:VIOLATES]->(SafetyConstraint)
//   (UnsafeControlAction)-[:CAN_LEAD_TO]->(Hazard)
//   (ControlStructure)-[:PROVIDES]->(UnsafeControlAction)
//   (LossScenario)-[:INVOLVES]->(UnsafeControlAction)
//   (SafetyConstraint)-[:ALLOCATED_TO]->(ControlStructure)
//
// Compliance relationships:
//   (Hazard|SafetyGoal|Requirement)-[:COMPLIES_WITH]->(StandardClause)
//
// ============================================================================
// END OF SCHEMA DEFINITION
// ============================================================================
