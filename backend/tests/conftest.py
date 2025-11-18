"""
Pytest configuration and fixtures for Safety Graph Twin tests.
"""

import pytest
from fastapi.testclient import TestClient
from neo4j import GraphDatabase

from app.core.config import get_settings
from app.db.neo4j_driver import Neo4jDriver, get_neo4j_driver, close_neo4j_driver
from app.main import app


# ============================================================================
# Session Fixtures (run once per test session)
# ============================================================================

@pytest.fixture(scope="session")
def test_settings():
    """Get test settings."""
    settings = get_settings()
    # Override for test environment if needed
    return settings


@pytest.fixture(scope="session")
def neo4j_session_driver(test_settings):
    """
    Create a Neo4j driver for the test session.

    This driver is reused across all tests in the session.
    """
    driver = GraphDatabase.driver(
        test_settings.neo4j_uri,
        auth=(test_settings.neo4j_user, test_settings.neo4j_password)
    )

    yield driver

    driver.close()


# ============================================================================
# Function Fixtures (run once per test function)
# ============================================================================

@pytest.fixture
def clean_database(neo4j_session_driver):
    """
    Clean the database before each test.

    WARNING: This deletes all data in the database!
    Only use with a test database, never production!
    """
    with neo4j_session_driver.session() as session:
        # Delete all nodes and relationships
        session.run("MATCH (n) DETACH DELETE n")

    yield

    # Optional: Clean up after test as well
    # with neo4j_session_driver.session() as session:
    #     session.run("MATCH (n) DETACH DELETE n")


@pytest.fixture
def neo4j_driver(clean_database):
    """Get Neo4j driver instance for testing."""
    driver = get_neo4j_driver()
    yield driver
    # Don't close the driver - it's a singleton managed by the application


@pytest.fixture
def api_client():
    """Get FastAPI test client."""
    client = TestClient(app)
    yield client


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_hazard():
    """Sample hazard data for testing."""
    return {
        "id": "H-TEST-001",
        "description": "Test hazard for unit testing",
        "asil": "D",
        "severity": 3,
        "exposure": 4,
        "controllability": 3
    }


@pytest.fixture
def sample_safety_goal():
    """Sample safety goal data for testing."""
    return {
        "id": "SG-TEST-001",
        "description": "Test safety goal for unit testing",
        "asil": "D",
        "safe_state": "Enter safe mode",
        "fault_tolerance_time": 100
    }


@pytest.fixture
def sample_component():
    """Sample component data for testing."""
    return {
        "id": "C-TEST-001",
        "name": "Test Component",
        "description": "Test component for unit testing",
        "component_type": "hardware",
        "supplier": "Test Supplier",
        "part_number": "TEST-001",
        "version": "1.0"
    }


@pytest.fixture
def sample_fsr():
    """Sample FSR data for testing."""
    return {
        "id": "FSR-TEST-001",
        "text": "Test FSR for unit testing",
        "asil": "D",
        "requirement_type": "safety_mechanism",
        "status": "approved"
    }


@pytest.fixture
def sample_tsr():
    """Sample TSR data for testing."""
    return {
        "id": "TSR-TEST-001",
        "text": "Test TSR for unit testing",
        "asil": "D",
        "requirement_type": "implementation",
        "status": "approved",
        "verification_method": "Unit test"
    }


@pytest.fixture
def sample_test_case():
    """Sample test case data for testing."""
    return {
        "id": "TC-TEST-001",
        "name": "Test case for unit testing",
        "description": "Test test case",
        "test_type": "unit",
        "status": "passed",
        "pass_criteria": "Test passes",
        "coverage_level": "statement"
    }


@pytest.fixture
def sample_hara_import():
    """Sample HARA import request for testing."""
    return {
        "hazards": [
            {
                "id": "H-TEST-001",
                "description": "Test hazard 1",
                "asil": "D"
            },
            {
                "id": "H-TEST-002",
                "description": "Test hazard 2",
                "asil": "C"
            }
        ],
        "scenarios": [
            {
                "id": "SC-TEST-001",
                "name": "Test scenario",
                "description": "Test operating scenario"
            }
        ],
        "safety_goals": [
            {
                "id": "SG-TEST-001",
                "description": "Test safety goal",
                "asil": "D"
            }
        ],
        "relationships": {
            "OCCURS_IN": [["H-TEST-001", "SC-TEST-001"]],
            "MITIGATED_BY": [["H-TEST-001", "SG-TEST-001"]]
        }
    }


@pytest.fixture
def sample_fmea_import():
    """Sample FMEA import request for testing."""
    return {
        "components": [
            {
                "id": "C-TEST-001",
                "name": "Test Component",
                "component_type": "hardware"
            }
        ],
        "failure_modes": [
            {
                "id": "FM-TEST-001",
                "description": "Test failure mode",
                "category": "electrical"
            }
        ],
        "fmea_entries": [
            {
                "id": "FMEA-TEST-001",
                "function_description": "Test function",
                "potential_failure": "Test failure",
                "severity": 8,
                "occurrence": 3,
                "detection": 4,
                "rpn": 96
            }
        ],
        "relationships": {
            "HAS_FAILURE_MODE": [["C-TEST-001", "FM-TEST-001"]],
            "ANALYZED_IN": [["FM-TEST-001", "FMEA-TEST-001"]]
        }
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def create_test_node(neo4j_driver):
    """
    Factory fixture to create test nodes in the database.

    Usage:
        def test_something(create_test_node):
            node = create_test_node("Hazard", {"id": "H-001", "description": "Test"})
    """
    def _create_node(label: str, properties: dict):
        query = f"""
        CREATE (n:{label} $properties)
        RETURN n
        """
        result = neo4j_driver.execute_write_transaction(query, {"properties": properties})
        return result[0]["n"] if result else None

    return _create_node


@pytest.fixture
def create_test_relationship(neo4j_driver):
    """
    Factory fixture to create test relationships in the database.

    Usage:
        def test_something(create_test_relationship):
            rel = create_test_relationship("H-001", "SG-001", "MITIGATED_BY")
    """
    def _create_relationship(source_id: str, target_id: str, rel_type: str):
        query = f"""
        MATCH (a {{id: $source_id}})
        MATCH (b {{id: $target_id}})
        CREATE (a)-[r:{rel_type}]->(b)
        RETURN r
        """
        result = neo4j_driver.execute_write_transaction(
            query,
            {"source_id": source_id, "target_id": target_id}
        )
        return result[0]["r"] if result else None

    return _create_relationship


# ============================================================================
# Markers for Test Organization
# ============================================================================

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (requires database)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running tests"
    )
    config.addinivalue_line(
        "markers", "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "service: Service layer tests"
    )
    config.addinivalue_line(
        "markers", "db: Database tests"
    )
