# Database Module

This module provides Neo4j database connectivity and query management.

## Structure

```
db/
├── __init__.py          # Module exports
├── neo4j_driver.py      # Database driver and connection management
├── queries.py           # Cypher query templates
└── README.md            # This file
```

## Files

### `neo4j_driver.py`

Provides singleton Neo4j driver manager with:

**Key Features:**
- Singleton pattern for global driver instance
- Connection pooling (configurable pool size)
- Health checks and connectivity verification
- Session management with context managers
- Transaction support (read/write)
- Schema inspection utilities

**Usage:**

```python
from app.db.neo4j_driver import get_neo4j_driver

# Get driver instance
driver = get_neo4j_driver()

# Execute simple query
results = driver.execute_query(
    "MATCH (h:Hazard {asil: $asil}) RETURN h",
    parameters={"asil": "D"}
)

# Execute write transaction
driver.execute_write_transaction(
    "CREATE (h:Hazard {id: $id, description: $desc})",
    parameters={"id": "H-001", "desc": "Unintended acceleration"}
)

# Use session context manager
with driver.get_session() as session:
    result = session.run("MATCH (n) RETURN count(n)")
    count = result.single()[0]

# Health check
health = driver.health_check()
if health["status"] == "healthy":
    print("Database is healthy")
```

**Methods:**

- `execute_query(query, parameters, database)`: Execute read query
- `execute_write_transaction(query, parameters, database)`: Execute write query in transaction
- `execute_read_transaction(query, parameters, database)`: Execute read query in transaction
- `get_session(database)`: Get session context manager
- `health_check()`: Check database connectivity
- `get_schema_info()`: Get constraints and indexes
- `get_node_counts()`: Get node counts by label
- `get_relationship_counts()`: Get relationship counts by type

### `queries.py`

Contains all Cypher query templates organized by function:

**Query Categories:**

1. **Node Creation**: `CREATE_HAZARD`, `CREATE_COMPONENT`, etc.
2. **Relationship Creation**: `CREATE_RELATIONSHIP`, `CREATE_RELATIONSHIP_WITH_METADATA`
3. **Batch Operations**: `BATCH_CREATE_NODES`, `BATCH_CREATE_RELATIONSHIPS`
4. **Hazard Coverage**: `GET_HAZARD_COVERAGE`, `GET_ALL_HAZARDS_COVERAGE`
5. **Impact Analysis**: `GET_COMPONENT_IMPACT`, `GET_ALL_COMPONENTS_IMPACT`
6. **Traceability**: `GET_TRACEABILITY_CHAIN`, `GET_REQUIREMENT_TRACEABILITY`
7. **Statistics**: `GET_NODE_STATISTICS`, `GET_ASIL_DISTRIBUTION`
8. **Search**: `SEARCH_NODES_BY_TEXT`, `SEARCH_HAZARDS`
9. **Filters**: `FILTER_BY_ASIL`, `FILTER_COMPONENTS_BY_TYPE`
10. **Updates**: `UPDATE_NODE`, `UPDATE_TEST_STATUS`
11. **Deletion**: `DELETE_NODE`, `DELETE_RELATIONSHIP`

**Usage:**

```python
from app.db.neo4j_driver import get_neo4j_driver
from app.db.queries import CREATE_HAZARD, GET_HAZARD_COVERAGE

driver = get_neo4j_driver()

# Create hazard
hazard_data = {
    "id": "H-001",
    "description": "Unintended acceleration",
    "asil": "D",
    "severity": 3,
    "exposure": 4,
    "controllability": 3
}
result = driver.execute_write_transaction(CREATE_HAZARD, hazard_data)

# Get hazard coverage
coverage = driver.execute_query(
    GET_HAZARD_COVERAGE,
    parameters={"hazard_id": "H-001"}
)
```

**Utility Functions:**

- `build_node_properties(data)`: Filter None values from properties
- `build_batch_nodes(nodes, label)`: Format nodes for batch creation
- `build_batch_relationships(relationships)`: Format relationships for batch creation

## Query Patterns

### Creating Nodes

All node creation queries follow the same pattern:

```cypher
CREATE (n:NodeLabel {
    id: $id,
    property1: $property1,
    property2: $property2,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n
```

**Example:**

```python
from app.db.queries import CREATE_COMPONENT

component_data = {
    "id": "C-INV-001",
    "name": "Inverter Gate Driver",
    "description": "High-side gate driver for IGBT",
    "component_type": "hardware",
    "supplier": "Infineon",
    "part_number": "1ED020I12-F2",
    "version": "Rev A"
}

driver.execute_write_transaction(CREATE_COMPONENT, component_data)
```

### Creating Relationships

Simple relationship creation:

```python
from app.db.queries import CREATE_RELATIONSHIP

relationship_data = {
    "source_id": "C-INV-001",
    "target_id": "F-TORQUE-CTRL",
    "rel_type": "IMPLEMENTS"
}

driver.execute_write_transaction(CREATE_RELATIONSHIP, relationship_data)
```

With metadata:

```python
from app.db.queries import CREATE_RELATIONSHIP_WITH_METADATA

relationship_data = {
    "source_id": "H-001",
    "target_id": "SG-001",
    "rel_type": "MITIGATED_BY",
    "created_by": "system",
    "rationale": "Derived from HARA analysis"
}

driver.execute_write_transaction(CREATE_RELATIONSHIP_WITH_METADATA, relationship_data)
```

### Batch Creation

For importing large datasets, use batch queries:

```python
from app.db.queries import BATCH_CREATE_NODES, build_batch_nodes

hazards = [
    {"id": "H-001", "description": "Unintended acceleration", "asil": "D"},
    {"id": "H-002", "description": "Loss of braking", "asil": "D"},
    {"id": "H-003", "description": "Steering failure", "asil": "C"}
]

batch_data = build_batch_nodes(hazards, "Hazard")
result = driver.execute_write_transaction(
    BATCH_CREATE_NODES,
    parameters={"nodes": batch_data}
)
```

### Hazard Coverage Analysis

Get coverage for a single hazard:

```python
from app.db.queries import GET_HAZARD_COVERAGE

coverage = driver.execute_query(
    GET_HAZARD_COVERAGE,
    parameters={"hazard_id": "H-001"}
)

# Result structure:
# {
#     "hazard": HazardNode,
#     "safety_goals": [SafetyGoalNode, ...],
#     "fsrs": [FSRNode, ...],
#     "tsrs": [TSRNode, ...],
#     "test_cases": [TestCaseNode, ...],
#     "complete_chains": int,
#     "coverage_status": "full" | "partial" | "none"
# }
```

Get coverage for all hazards:

```python
from app.db.queries import GET_ALL_HAZARDS_COVERAGE

all_coverage = driver.execute_query(GET_ALL_HAZARDS_COVERAGE)

for hazard_coverage in all_coverage:
    print(f"{hazard_coverage['hazard_id']}: {hazard_coverage['coverage_status']}")
```

Get coverage statistics:

```python
from app.db.queries import GET_COVERAGE_STATISTICS

stats = driver.execute_query(GET_COVERAGE_STATISTICS)[0]

# Result:
# {
#     "total_hazards": 50,
#     "fully_covered": 35,
#     "partially_covered": 10,
#     "not_covered": 5,
#     "coverage_percentage": 70.0
# }
```

### Component Impact Analysis

Analyze impact of a single component:

```python
from app.db.queries import GET_COMPONENT_IMPACT

impact = driver.execute_query(
    GET_COMPONENT_IMPACT,
    parameters={"component_id": "C-INV-001"}
)

# Result structure:
# {
#     "component": ComponentNode,
#     "hazards": [HazardNode, ...],
#     "safety_goals": [SafetyGoalNode, ...],
#     "functions": [FunctionNode, ...],
#     "test_cases": [TestCaseNode, ...],
#     "failure_modes": [FailureModeNode, ...],
#     "fmea_entries": [FMEAEntryNode, ...],
#     "defects": [DefectInstanceNode, ...],
#     "impact_score": int
# }
```

Get impact for all components (ranked):

```python
from app.db.queries import GET_ALL_COMPONENTS_IMPACT

all_impacts = driver.execute_query(GET_ALL_COMPONENTS_IMPACT)

for component_impact in all_impacts[:10]:  # Top 10
    print(f"{component_impact['component_id']}: score={component_impact['impact_score']}")
```

### Traceability Chains

Get complete traceability chain for a hazard:

```python
from app.db.queries import GET_TRACEABILITY_CHAIN

chains = driver.execute_query(
    GET_TRACEABILITY_CHAIN,
    parameters={"hazard_id": "H-001"}
)

for chain in chains:
    print(f"Hazard: {chain['hazard']['id']}")
    print(f"  -> SafetyGoal: {chain['safety_goal']['id']}")
    print(f"  -> FSR: {chain['fsr']['id']}")
    print(f"  -> TSR: {chain['tsr']['id']}")
    print(f"  -> TestCase: {chain['test_case']['id']}")
```

### Statistics

Get node counts:

```python
from app.db.queries import GET_NODE_STATISTICS

stats = driver.execute_query(GET_NODE_STATISTICS)

for stat in stats:
    print(f"{stat['label']}: {stat['count']}")
```

Get ASIL distribution:

```python
from app.db.queries import GET_ASIL_DISTRIBUTION

distribution = driver.execute_query(GET_ASIL_DISTRIBUTION)

for entry in distribution:
    print(f"{entry['node_type']} - ASIL {entry['asil']}: {entry['count']}")
```

### Search

Full-text search:

```python
from app.db.queries import SEARCH_NODES_BY_TEXT

results = driver.execute_query(
    SEARCH_NODES_BY_TEXT,
    parameters={
        "index_name": "hazard_description_idx",
        "search_text": "acceleration",
        "limit": 10
    }
)
```

Simple text search:

```python
from app.db.queries import SEARCH_HAZARDS

hazards = driver.execute_query(
    SEARCH_HAZARDS,
    parameters={"search_text": "braking", "limit": 20}
)
```

### Filters

Filter by ASIL:

```python
from app.db.queries import FILTER_HAZARDS_BY_ASIL

critical_hazards = driver.execute_query(
    FILTER_HAZARDS_BY_ASIL,
    parameters={"asil_levels": ["C", "D"]}
)
```

Filter by component type:

```python
from app.db.queries import FILTER_COMPONENTS_BY_TYPE

hw_components = driver.execute_query(
    FILTER_COMPONENTS_BY_TYPE,
    parameters={"component_type": "hardware"}
)
```

### Updates

Update node properties:

```python
from app.db.queries import UPDATE_NODE

driver.execute_write_transaction(
    UPDATE_NODE,
    parameters={
        "node_id": "H-001",
        "properties": {
            "description": "Updated description",
            "severity": 3
        }
    }
)
```

Update test status:

```python
from app.db.queries import UPDATE_TEST_STATUS

driver.execute_write_transaction(
    UPDATE_TEST_STATUS,
    parameters={
        "test_id": "TC-045",
        "status": "passed",
        "result": "All assertions passed"
    }
)
```

## Best Practices

### 1. Use Transactions for Writes

Always use write transactions for data modifications:

```python
# Good
driver.execute_write_transaction(CREATE_HAZARD, hazard_data)

# Avoid (no transaction guarantee)
driver.execute_query(CREATE_HAZARD, hazard_data)
```

### 2. Use Parameterized Queries

Never concatenate user input into queries:

```python
# Good
driver.execute_query(
    "MATCH (h:Hazard {id: $id}) RETURN h",
    parameters={"id": hazard_id}
)

# BAD - SQL injection risk!
driver.execute_query(f"MATCH (h:Hazard {{id: '{hazard_id}'}}) RETURN h")
```

### 3. Use Batch Operations for Large Datasets

For importing many nodes/relationships, use batch queries:

```python
# Good for 1000+ nodes
batch_data = build_batch_nodes(nodes, "Hazard")
driver.execute_write_transaction(BATCH_CREATE_NODES, {"nodes": batch_data})

# Avoid for large datasets (too many round trips)
for node in nodes:
    driver.execute_write_transaction(CREATE_HAZARD, node)
```

### 4. Filter None Values

Use `build_node_properties()` to exclude None values:

```python
from app.db.queries import build_node_properties

data = {
    "id": "H-001",
    "description": "Test",
    "asil": "D",
    "severity": None  # Optional field not provided
}

properties = build_node_properties(data)
# Result: {"id": "H-001", "description": "Test", "asil": "D"}
```

### 5. Handle Empty Results

Always check for empty results:

```python
results = driver.execute_query(GET_HAZARD_COVERAGE, {"hazard_id": "H-999"})

if not results:
    # Hazard not found
    raise ValueError("Hazard not found")

coverage = results[0]
```

### 6. Use Session Context Managers

For multiple operations, use session context managers:

```python
with driver.get_session() as session:
    # Multiple operations in same session
    session.run(CREATE_HAZARD, hazard_data)
    session.run(CREATE_RELATIONSHIP, relationship_data)
```

## Error Handling

### Connection Errors

```python
from neo4j.exceptions import ServiceUnavailable

try:
    driver = get_neo4j_driver()
    results = driver.execute_query("MATCH (n) RETURN count(n)")
except ServiceUnavailable as e:
    logger.error(f"Cannot connect to Neo4j: {e}")
    # Retry or return error to user
```

### Authentication Errors

```python
from neo4j.exceptions import AuthError

try:
    driver = get_neo4j_driver()
except AuthError as e:
    logger.error(f"Authentication failed: {e}")
    # Check credentials in .env file
```

### Query Errors

```python
from neo4j.exceptions import Neo4jError

try:
    results = driver.execute_query(
        "MATCH (h:Hazard {id: $id}) RETURN h",
        parameters={"id": "H-001"}
    )
except Neo4jError as e:
    logger.error(f"Query failed: {e.message} (code: {e.code})")
    # Handle specific error codes
```

## Performance Tips

### 1. Use Indexes

Ensure indexes exist for frequently queried properties (done via `init_schema.py`):

```cypher
CREATE INDEX hazard_asil_idx IF NOT EXISTS
FOR (n:Hazard) ON (n.asil);
```

### 2. Use EXPLAIN/PROFILE

Profile slow queries:

```python
result = driver.execute_query("EXPLAIN MATCH (h:Hazard) RETURN h")
# Review execution plan
```

### 3. Limit Result Sets

Always use LIMIT for potentially large result sets:

```python
# Good
SEARCH_HAZARDS = """
MATCH (h:Hazard)
WHERE h.description CONTAINS $search_text
RETURN h
LIMIT $limit  -- Always limit
"""

# Avoid (could return millions of rows)
"MATCH (h:Hazard) RETURN h"
```

### 4. Use Connection Pooling

Connection pooling is configured in `config.py`:

```python
neo4j_max_connection_pool_size: int = 50  # Adjust based on load
```

## Testing

### Unit Tests

Test query templates:

```python
from app.db.queries import CREATE_HAZARD

def test_create_hazard_query():
    """Test hazard creation query template."""
    assert "CREATE (n:Hazard" in CREATE_HAZARD
    assert "id: $id" in CREATE_HAZARD
    assert "RETURN n" in CREATE_HAZARD
```

### Integration Tests

Test actual database operations:

```python
import pytest
from app.db.neo4j_driver import get_neo4j_driver
from app.db.queries import CREATE_HAZARD, GET_HAZARD_COVERAGE

@pytest.fixture
def driver():
    return get_neo4j_driver()

def test_create_and_query_hazard(driver):
    """Test creating hazard and querying it."""
    # Create hazard
    hazard_data = {
        "id": "H-TEST-001",
        "description": "Test hazard",
        "asil": "D"
    }
    driver.execute_write_transaction(CREATE_HAZARD, hazard_data)

    # Query it back
    results = driver.execute_query(
        "MATCH (h:Hazard {id: $id}) RETURN h",
        parameters={"id": "H-TEST-001"}
    )

    assert len(results) == 1
    assert results[0]["h"]["description"] == "Test hazard"

    # Cleanup
    driver.execute_write_transaction(
        "MATCH (h:Hazard {id: $id}) DETACH DELETE h",
        parameters={"id": "H-TEST-001"}
    )
```

---

**Last Updated**: 2025-11-18
**Version**: 1.0 (M1.4)
