"""
Unit tests for HARA import service.
"""

import pytest

from app.models.schemas import HARAImportRequest
from app.models.nodes import HazardNode, ScenarioNode, SafetyGoalNode
from app.services.hara_import import HARAImportService


@pytest.mark.unit
@pytest.mark.service
class TestHARAImportService:
    """Test cases for HARA import service."""

    def test_service_initialization(self, neo4j_driver):
        """Test service can be initialized."""
        service = HARAImportService(driver=neo4j_driver)
        assert service is not None
        assert service.driver == neo4j_driver

    def test_import_hazards_only(self, clean_database, neo4j_driver):
        """Test importing only hazards."""
        service = HARAImportService(driver=neo4j_driver)

        request = HARAImportRequest(
            hazards=[
                HazardNode(
                    id="H-TEST-001",
                    description="Test hazard",
                    asil="D"
                )
            ],
            scenarios=[],
            safety_goals=[],
            relationships={}
        )

        result = service.import_hara(request)

        assert result.status == "success"
        assert result.data["hazards_created"] == 1
        assert result.data["scenarios_created"] == 0
        assert result.data["safety_goals_created"] == 0

    def test_import_complete_hara(self, clean_database, neo4j_driver):
        """Test importing complete HARA dataset."""
        service = HARAImportService(driver=neo4j_driver)

        request = HARAImportRequest(
            hazards=[
                HazardNode(
                    id="H-TEST-001",
                    description="Test hazard",
                    asil="D",
                    severity=3,
                    exposure=4,
                    controllability=3
                )
            ],
            scenarios=[
                ScenarioNode(
                    id="SC-TEST-001",
                    name="Test scenario",
                    description="Test operating scenario"
                )
            ],
            safety_goals=[
                SafetyGoalNode(
                    id="SG-TEST-001",
                    description="Test safety goal",
                    asil="D"
                )
            ],
            relationships={
                "OCCURS_IN": [["H-TEST-001", "SC-TEST-001"]],
                "MITIGATED_BY": [["H-TEST-001", "SG-TEST-001"]]
            }
        )

        result = service.import_hara(request)

        assert result.status == "success"
        assert result.data["hazards_created"] == 1
        assert result.data["scenarios_created"] == 1
        assert result.data["safety_goals_created"] == 1
        assert result.data["relationships_created"] == 2

    def test_import_multiple_hazards(self, clean_database, neo4j_driver):
        """Test importing multiple hazards."""
        service = HARAImportService(driver=neo4j_driver)

        hazards = [
            HazardNode(id=f"H-TEST-{i:03d}", description=f"Test hazard {i}", asil="D")
            for i in range(1, 6)
        ]

        request = HARAImportRequest(
            hazards=hazards,
            scenarios=[],
            safety_goals=[],
            relationships={}
        )

        result = service.import_hara(request)

        assert result.status == "success"
        assert result.data["hazards_created"] == 5

    def test_import_with_various_asil_levels(self, clean_database, neo4j_driver):
        """Test importing hazards with different ASIL levels."""
        service = HARAImportService(driver=neo4j_driver)

        hazards = [
            HazardNode(id="H-TEST-A", description="ASIL A hazard", asil="A"),
            HazardNode(id="H-TEST-B", description="ASIL B hazard", asil="B"),
            HazardNode(id="H-TEST-C", description="ASIL C hazard", asil="C"),
            HazardNode(id="H-TEST-D", description="ASIL D hazard", asil="D"),
            HazardNode(id="H-TEST-QM", description="QM hazard", asil="QM"),
        ]

        request = HARAImportRequest(
            hazards=hazards,
            scenarios=[],
            safety_goals=[],
            relationships={}
        )

        result = service.import_hara(request)

        assert result.status == "success"
        assert result.data["hazards_created"] == 5

    def test_import_validates_safety_goal_asil(self, clean_database, neo4j_driver):
        """Test that safety goals cannot have ASIL QM."""
        service = HARAImportService(driver=neo4j_driver)

        # Safety goal with QM should fail validation at Pydantic level
        with pytest.raises(Exception):  # Pydantic ValidationError
            request = HARAImportRequest(
                hazards=[],
                scenarios=[],
                safety_goals=[
                    SafetyGoalNode(
                        id="SG-TEST-001",
                        description="Invalid safety goal",
                        asil="QM"  # This should fail validation
                    )
                ],
                relationships={}
            )

    def test_import_empty_request(self, clean_database, neo4j_driver):
        """Test importing empty request."""
        service = HARAImportService(driver=neo4j_driver)

        request = HARAImportRequest(
            hazards=[],
            scenarios=[],
            safety_goals=[],
            relationships={}
        )

        result = service.import_hara(request)

        assert result.status == "success"
        assert result.data["hazards_created"] == 0
        assert result.data["scenarios_created"] == 0
        assert result.data["safety_goals_created"] == 0
        assert result.data["relationships_created"] == 0

    def test_import_with_optional_fields(self, clean_database, neo4j_driver):
        """Test importing hazards with optional fields."""
        service = HARAImportService(driver=neo4j_driver)

        request = HARAImportRequest(
            hazards=[
                HazardNode(
                    id="H-TEST-001",
                    description="Hazard with all fields",
                    asil="D",
                    severity=3,
                    exposure=4,
                    controllability=3
                ),
                HazardNode(
                    id="H-TEST-002",
                    description="Hazard with minimal fields",
                    asil="C"
                    # No severity, exposure, controllability
                )
            ],
            scenarios=[],
            safety_goals=[],
            relationships={}
        )

        result = service.import_hara(request)

        assert result.status == "success"
        assert result.data["hazards_created"] == 2

    def test_import_creates_traceability_chain(self, clean_database, neo4j_driver):
        """Test that import creates proper traceability chain."""
        service = HARAImportService(driver=neo4j_driver)

        request = HARAImportRequest(
            hazards=[
                HazardNode(id="H-TEST-001", description="Test hazard", asil="D")
            ],
            scenarios=[
                ScenarioNode(id="SC-TEST-001", name="Test scenario", description="Test")
            ],
            safety_goals=[
                SafetyGoalNode(id="SG-TEST-001", description="Test safety goal", asil="D")
            ],
            relationships={
                "OCCURS_IN": [["H-TEST-001", "SC-TEST-001"]],
                "MITIGATED_BY": [["H-TEST-001", "SG-TEST-001"]]
            }
        )

        result = service.import_hara(request)
        assert result.status == "success"

        # Verify relationships exist in database
        query = """
        MATCH (h:Hazard {id: 'H-TEST-001'})-[:MITIGATED_BY]->(sg:SafetyGoal {id: 'SG-TEST-001'})
        RETURN h, sg
        """
        results = neo4j_driver.execute_query(query)
        assert len(results) == 1

        query = """
        MATCH (h:Hazard {id: 'H-TEST-001'})-[:OCCURS_IN]->(sc:Scenario {id: 'SC-TEST-001'})
        RETURN h, sc
        """
        results = neo4j_driver.execute_query(query)
        assert len(results) == 1
