"""
Core Cypher queries for Safety Graph Twin.

This module contains all Cypher query templates used for:
- Creating nodes and relationships
- Querying hazard coverage chains
- Analyzing component impact
- Computing statistics and metrics
"""

from typing import Dict, Any, List


# ==============================================================================
# NODE CREATION QUERIES
# ==============================================================================

CREATE_ITEM = """
CREATE (n:Item {
    id: $id,
    name: $name,
    description: $description,
    item_type: $item_type,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_FUNCTION = """
CREATE (n:Function {
    id: $id,
    name: $name,
    description: $description,
    function_type: $function_type,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_COMPONENT = """
CREATE (n:Component {
    id: $id,
    name: $name,
    description: $description,
    component_type: $component_type,
    supplier: $supplier,
    part_number: $part_number,
    version: $version,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_SIGNAL = """
CREATE (n:Signal {
    id: $id,
    name: $name,
    description: $description,
    signal_type: $signal_type,
    unit: $unit,
    range_min: $range_min,
    range_max: $range_max,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_HAZARD = """
CREATE (n:Hazard {
    id: $id,
    description: $description,
    asil: $asil,
    severity: $severity,
    exposure: $exposure,
    controllability: $controllability,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_SCENARIO = """
CREATE (n:Scenario {
    id: $id,
    name: $name,
    description: $description,
    operating_mode: $operating_mode,
    environment: $environment,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_SAFETY_GOAL = """
CREATE (n:SafetyGoal {
    id: $id,
    description: $description,
    asil: $asil,
    safe_state: $safe_state,
    fault_tolerance_time: $fault_tolerance_time,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_FSR = """
CREATE (n:FunctionalSafetyRequirement {
    id: $id,
    text: $text,
    asil: $asil,
    requirement_type: $requirement_type,
    status: $status,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_TSR = """
CREATE (n:TechnicalSafetyRequirement {
    id: $id,
    text: $text,
    asil: $asil,
    asil_decomposition: $asil_decomposition,
    requirement_type: $requirement_type,
    status: $status,
    verification_method: $verification_method,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_FMEA_ENTRY = """
CREATE (n:FMEAEntry {
    id: $id,
    function_description: $function_description,
    potential_failure: $potential_failure,
    effect: $effect,
    cause: $cause,
    current_controls: $current_controls,
    severity: $severity,
    occurrence: $occurrence,
    detection: $detection,
    rpn: $rpn,
    recommended_action: $recommended_action,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_FAILURE_MODE = """
CREATE (n:FailureMode {
    id: $id,
    description: $description,
    category: $category,
    probability: $probability,
    detection_mechanism: $detection_mechanism,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_FT_EVENT = """
CREATE (n:FTEvent {
    id: $id,
    description: $description,
    event_type: $event_type,
    gate_type: $gate_type,
    probability: $probability,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_TEST_CASE = """
CREATE (n:TestCase {
    id: $id,
    name: $name,
    description: $description,
    test_type: $test_type,
    status: $status,
    pass_criteria: $pass_criteria,
    coverage_level: $coverage_level,
    last_run: $last_run,
    result: $result,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_DEFECT = """
CREATE (n:DefectInstance {
    id: $id,
    title: $title,
    description: $description,
    severity: $severity,
    status: $status,
    source: $source,
    detected_date: $detected_date,
    resolved_date: $resolved_date,
    root_cause: $root_cause,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_UCA = """
CREATE (n:UnsafeControlAction {
    id: $id,
    description: $description,
    control_action: $control_action,
    context: $context,
    hazard_link: $hazard_link,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_CONTROL_STRUCTURE = """
CREATE (n:ControlStructure {
    id: $id,
    name: $name,
    description: $description,
    controller_type: $controller_type,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_LOSS_SCENARIO = """
CREATE (n:LossScenario {
    id: $id,
    description: $description,
    causal_factors: $causal_factors,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_SAFETY_CONSTRAINT = """
CREATE (n:SafetyConstraint {
    id: $id,
    description: $description,
    constraint_type: $constraint_type,
    rationale: $rationale,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""

CREATE_STANDARD_CLAUSE = """
CREATE (n:StandardClause {
    id: $id,
    standard: $standard,
    clause_number: $clause_number,
    title: $title,
    description: $description,
    requirements: $requirements,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
"""


# ==============================================================================
# RELATIONSHIP CREATION QUERIES
# ==============================================================================

CREATE_RELATIONSHIP = """
MATCH (a {id: $source_id})
MATCH (b {id: $target_id})
CREATE (a)-[r:$rel_type $properties]->(b)
RETURN r
"""

# Parametrized relationship creation with metadata
CREATE_RELATIONSHIP_WITH_METADATA = """
MATCH (a {id: $source_id})
MATCH (b {id: $target_id})
CREATE (a)-[r:$rel_type {
    created_at: datetime(),
    created_by: $created_by,
    rationale: $rationale
}]->(b)
RETURN r
"""


# ==============================================================================
# BATCH CREATION QUERIES
# ==============================================================================

BATCH_CREATE_NODES = """
UNWIND $nodes AS node
CALL apoc.create.node([node.label], node.properties) YIELD node AS n
RETURN count(n) AS created_count
"""

BATCH_CREATE_RELATIONSHIPS = """
UNWIND $relationships AS rel
MATCH (a {id: rel.source_id})
MATCH (b {id: rel.target_id})
CALL apoc.create.relationship(a, rel.type, rel.properties, b) YIELD rel AS r
RETURN count(r) AS created_count
"""


# ==============================================================================
# MERGE QUERIES (CREATE OR UPDATE)
# ==============================================================================

MERGE_NODE = """
MERGE (n:$label {id: $id})
ON CREATE SET n += $properties, n.created_at = datetime()
ON MATCH SET n += $properties, n.updated_at = datetime()
RETURN n
"""


# ==============================================================================
# HAZARD COVERAGE QUERIES
# ==============================================================================

GET_HAZARD_COVERAGE = """
MATCH (h:Hazard {id: $hazard_id})
OPTIONAL MATCH coverage_path = (h)-[:MITIGATED_BY]->(sg:SafetyGoal)
                               -[:REFINED_TO]->(fsr:FunctionalSafetyRequirement)
                               -[:REFINED_TO]->(tsr:TechnicalSafetyRequirement)
                               -[:VERIFIED_BY]->(tc:TestCase)
WITH h,
     collect(DISTINCT sg) AS safety_goals,
     collect(DISTINCT fsr) AS fsrs,
     collect(DISTINCT tsr) AS tsrs,
     collect(DISTINCT tc) AS test_cases,
     count(DISTINCT coverage_path) AS complete_chains
RETURN {
    hazard: h,
    safety_goals: safety_goals,
    fsrs: fsrs,
    tsrs: tsrs,
    test_cases: test_cases,
    complete_chains: complete_chains,
    coverage_status: CASE
        WHEN complete_chains > 0 THEN 'full'
        WHEN size(safety_goals) > 0 THEN 'partial'
        ELSE 'none'
    END
} AS coverage
"""

GET_ALL_HAZARDS_COVERAGE = """
MATCH (h:Hazard)
OPTIONAL MATCH (h)-[:MITIGATED_BY]->(sg:SafetyGoal)
                  -[:REFINED_TO]->(fsr:FunctionalSafetyRequirement)
                  -[:REFINED_TO]->(tsr:TechnicalSafetyRequirement)
                  -[:VERIFIED_BY]->(tc:TestCase)
WITH h,
     collect(DISTINCT sg.id) AS safety_goals,
     collect(DISTINCT fsr.id) AS fsrs,
     collect(DISTINCT tsr.id) AS tsrs,
     collect(DISTINCT tc.id) AS test_cases,
     count(DISTINCT tc) AS test_count
RETURN {
    hazard_id: h.id,
    description: h.description,
    asil: h.asil,
    safety_goals: safety_goals,
    fsrs: fsrs,
    tsrs: tsrs,
    test_cases: test_cases,
    coverage_status: CASE
        WHEN test_count > 0 THEN 'full'
        WHEN size(safety_goals) > 0 THEN 'partial'
        ELSE 'none'
    END
} AS coverage
ORDER BY h.asil DESC, h.id
"""

GET_COVERAGE_STATISTICS = """
MATCH (h:Hazard)
OPTIONAL MATCH (h)-[:MITIGATED_BY]->(sg:SafetyGoal)
                  -[:REFINED_TO]->(fsr:FunctionalSafetyRequirement)
                  -[:REFINED_TO]->(tsr:TechnicalSafetyRequirement)
                  -[:VERIFIED_BY]->(tc:TestCase)
WITH h, count(DISTINCT tc) AS test_count
WITH
    count(h) AS total_hazards,
    sum(CASE WHEN test_count > 0 THEN 1 ELSE 0 END) AS fully_covered,
    sum(CASE WHEN test_count = 0 THEN 1 ELSE 0 END) AS not_covered
RETURN {
    total_hazards: total_hazards,
    fully_covered: fully_covered,
    partially_covered: total_hazards - fully_covered - not_covered,
    not_covered: not_covered,
    coverage_percentage: CASE
        WHEN total_hazards > 0
        THEN toFloat(fully_covered) / total_hazards * 100
        ELSE 0
    END
} AS statistics
"""


# ==============================================================================
# COMPONENT IMPACT ANALYSIS QUERIES
# ==============================================================================

GET_COMPONENT_IMPACT = """
MATCH (c:Component {id: $component_id})
OPTIONAL MATCH (c)-[:IMPLEMENTS]->(f:Function)
                  -[:CONTRIBUTES_TO]->(sg:SafetyGoal)
                  <-[:MITIGATED_BY]-(h:Hazard)
OPTIONAL MATCH (c)-[:VERIFIED_BY]->(tc:TestCase)
OPTIONAL MATCH (c)-[:HAS_FAILURE_MODE]->(fm:FailureMode)
                  -[:ANALYZED_IN]->(fmea:FMEAEntry)
OPTIONAL MATCH (c)<-[:FOUND_IN]-(d:DefectInstance)
WITH c,
     collect(DISTINCT h) AS hazards,
     collect(DISTINCT sg) AS safety_goals,
     collect(DISTINCT f) AS functions,
     collect(DISTINCT tc) AS test_cases,
     collect(DISTINCT fm) AS failure_modes,
     collect(DISTINCT fmea) AS fmea_entries,
     collect(DISTINCT d) AS defects
RETURN {
    component: c,
    hazards: hazards,
    safety_goals: safety_goals,
    functions: functions,
    test_cases: test_cases,
    failure_modes: failure_modes,
    fmea_entries: fmea_entries,
    defects: defects,
    impact_score: size(hazards) * 10 + size(safety_goals) * 5 + size(failure_modes) * 3
} AS impact
"""

GET_ALL_COMPONENTS_IMPACT = """
MATCH (c:Component)
OPTIONAL MATCH (c)-[:IMPLEMENTS]->(f:Function)
                  -[:CONTRIBUTES_TO]->(sg:SafetyGoal)
                  <-[:MITIGATED_BY]-(h:Hazard)
OPTIONAL MATCH (c)-[:HAS_FAILURE_MODE]->(fm:FailureMode)
WITH c,
     count(DISTINCT h) AS hazard_count,
     count(DISTINCT sg) AS safety_goal_count,
     count(DISTINCT fm) AS failure_mode_count,
     max(h.asil) AS max_asil
RETURN {
    component_id: c.id,
    name: c.name,
    component_type: c.component_type,
    hazard_count: hazard_count,
    safety_goal_count: safety_goal_count,
    failure_mode_count: failure_mode_count,
    max_asil: max_asil,
    impact_score: hazard_count * 10 + safety_goal_count * 5 + failure_mode_count * 3
} AS impact
ORDER BY impact.impact_score DESC
"""


# ==============================================================================
# TRACEABILITY QUERIES
# ==============================================================================

GET_TRACEABILITY_CHAIN = """
MATCH path = (h:Hazard {id: $hazard_id})-[:MITIGATED_BY]->(sg:SafetyGoal)
                                       -[:REFINED_TO]->(fsr:FunctionalSafetyRequirement)
                                       -[:REFINED_TO]->(tsr:TechnicalSafetyRequirement)
                                       -[:VERIFIED_BY]->(tc:TestCase)
RETURN {
    hazard: h,
    safety_goal: sg,
    fsr: fsr,
    tsr: tsr,
    test_case: tc,
    path: path
} AS chain
"""

GET_REQUIREMENT_TRACEABILITY = """
MATCH (req {id: $requirement_id})
OPTIONAL MATCH upstream = (h:Hazard)-[:MITIGATED_BY]->(sg:SafetyGoal)-[:REFINED_TO*1..2]->(req)
OPTIONAL MATCH downstream = (req)-[:REFINED_TO|VERIFIED_BY*1..5]->(target)
RETURN {
    requirement: req,
    upstream_path: collect(DISTINCT upstream),
    downstream_nodes: collect(DISTINCT target)
} AS traceability
"""


# ==============================================================================
# STATISTICS QUERIES
# ==============================================================================

GET_NODE_STATISTICS = """
MATCH (n)
WITH labels(n) AS node_labels
UNWIND node_labels AS label
RETURN label, count(*) AS count
ORDER BY count DESC
"""

GET_RELATIONSHIP_STATISTICS = """
MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(*) AS count
ORDER BY count DESC
"""

GET_ASIL_DISTRIBUTION = """
MATCH (n)
WHERE n.asil IS NOT NULL
WITH labels(n)[0] AS node_type, n.asil AS asil
RETURN node_type, asil, count(*) AS count
ORDER BY node_type, asil
"""

GET_TEST_STATUS_STATISTICS = """
MATCH (tc:TestCase)
RETURN tc.status AS status, count(*) AS count
ORDER BY count DESC
"""

GET_DEFECT_STATISTICS = """
MATCH (d:DefectInstance)
RETURN {
    total: count(d),
    by_severity: [(d)-[:HAS_SEVERITY]->(s) | {severity: s.name, count: count(d)}],
    by_status: [(d)-[:HAS_STATUS]->(st) | {status: st.name, count: count(d)}],
    by_source: [(d)-[:FROM_SOURCE]->(src) | {source: src.name, count: count(d)}]
} AS statistics
"""

GET_DATABASE_SUMMARY = """
MATCH (n)
WITH count(n) AS total_nodes
MATCH ()-[r]->()
WITH total_nodes, count(r) AS total_relationships
MATCH (h:Hazard)
OPTIONAL MATCH (h)-[:MITIGATED_BY]->()-[:REFINED_TO*]->()-[:VERIFIED_BY]->(tc:TestCase)
WITH total_nodes, total_relationships,
     count(DISTINCT h) AS total_hazards,
     count(DISTINCT tc) AS verified_hazards
RETURN {
    total_nodes: total_nodes,
    total_relationships: total_relationships,
    total_hazards: total_hazards,
    verified_hazards: verified_hazards,
    coverage_percentage: CASE
        WHEN total_hazards > 0
        THEN toFloat(verified_hazards) / total_hazards * 100
        ELSE 0
    END
} AS summary
"""


# ==============================================================================
# SEARCH QUERIES
# ==============================================================================

SEARCH_NODES_BY_TEXT = """
CALL db.index.fulltext.queryNodes($index_name, $search_text)
YIELD node, score
RETURN node, score
ORDER BY score DESC
LIMIT $limit
"""

SEARCH_HAZARDS = """
MATCH (h:Hazard)
WHERE h.description CONTAINS $search_text
   OR h.id CONTAINS $search_text
RETURN h
ORDER BY h.asil DESC, h.id
LIMIT $limit
"""

SEARCH_REQUIREMENTS = """
MATCH (req)
WHERE (req:FunctionalSafetyRequirement OR req:TechnicalSafetyRequirement)
  AND (req.text CONTAINS $search_text OR req.id CONTAINS $search_text)
RETURN req
ORDER BY req.asil DESC, req.id
LIMIT $limit
"""

SEARCH_COMPONENTS = """
MATCH (c:Component)
WHERE c.name CONTAINS $search_text
   OR c.description CONTAINS $search_text
   OR c.id CONTAINS $search_text
RETURN c
ORDER BY c.name
LIMIT $limit
"""


# ==============================================================================
# FILTER QUERIES
# ==============================================================================

FILTER_BY_ASIL = """
MATCH (n)
WHERE n.asil = $asil
RETURN n
ORDER BY labels(n)[0], n.id
"""

FILTER_HAZARDS_BY_ASIL = """
MATCH (h:Hazard)
WHERE h.asil IN $asil_levels
RETURN h
ORDER BY h.asil DESC, h.id
"""

FILTER_COMPONENTS_BY_TYPE = """
MATCH (c:Component)
WHERE c.component_type = $component_type
RETURN c
ORDER BY c.name
"""

FILTER_TESTS_BY_STATUS = """
MATCH (tc:TestCase)
WHERE tc.status IN $statuses
RETURN tc
ORDER BY tc.status, tc.id
"""


# ==============================================================================
# DELETION QUERIES
# ==============================================================================

DELETE_NODE = """
MATCH (n {id: $node_id})
DETACH DELETE n
"""

DELETE_RELATIONSHIP = """
MATCH (a {id: $source_id})-[r:$rel_type]->(b {id: $target_id})
DELETE r
"""

DELETE_ALL_NODES_BY_LABEL = """
MATCH (n:$label)
DETACH DELETE n
"""

# WARNING: Use with extreme caution
DELETE_ALL = """
MATCH (n)
DETACH DELETE n
"""


# ==============================================================================
# UPDATE QUERIES
# ==============================================================================

UPDATE_NODE = """
MATCH (n {id: $node_id})
SET n += $properties, n.updated_at = datetime()
RETURN n
"""

UPDATE_TEST_STATUS = """
MATCH (tc:TestCase {id: $test_id})
SET tc.status = $status,
    tc.result = $result,
    tc.last_run = datetime(),
    tc.updated_at = datetime()
RETURN tc
"""

UPDATE_DEFECT_STATUS = """
MATCH (d:DefectInstance {id: $defect_id})
SET d.status = $status,
    d.resolved_date = CASE WHEN $status = 'resolved' THEN datetime() ELSE d.resolved_date END,
    d.updated_at = datetime()
RETURN d
"""


# ==============================================================================
# GRAPH ANALYTICS QUERIES (Phase 4)
# ==============================================================================

GET_COMPONENT_CENTRALITY = """
CALL gds.graph.project(
    'component-graph',
    'Component',
    {
        IMPLEMENTS: {orientation: 'UNDIRECTED'},
        DEPENDS_ON: {orientation: 'UNDIRECTED'}
    }
)
CALL gds.degree.stream('component-graph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS component_id, score AS degree_centrality
ORDER BY degree_centrality DESC
"""

GET_CRITICAL_PATHS = """
MATCH path = shortestPath((h:Hazard)-[*]-(tc:TestCase))
WHERE h.asil IN ['C', 'D']
RETURN path, length(path) AS path_length
ORDER BY path_length
LIMIT 10
"""


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def build_node_properties(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build node properties dictionary, excluding None values.

    Args:
        data: Raw data dictionary from Pydantic model

    Returns:
        Filtered properties dictionary
    """
    return {k: v for k, v in data.items() if v is not None}


def build_batch_nodes(nodes: List[Dict[str, Any]], label: str) -> List[Dict[str, Any]]:
    """
    Build batch nodes list for UNWIND query.

    Args:
        nodes: List of node data dictionaries
        label: Node label

    Returns:
        List formatted for batch creation
    """
    return [
        {
            "label": label,
            "properties": build_node_properties(node)
        }
        for node in nodes
    ]


def build_batch_relationships(
    relationships: List[tuple[str, str, str, Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    Build batch relationships list for UNWIND query.

    Args:
        relationships: List of (source_id, target_id, rel_type, properties) tuples

    Returns:
        List formatted for batch creation
    """
    return [
        {
            "source_id": source,
            "target_id": target,
            "type": rel_type,
            "properties": props or {}
        }
        for source, target, rel_type, props in relationships
    ]
