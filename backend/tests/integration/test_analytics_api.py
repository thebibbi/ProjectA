"""
Integration tests for analytics API endpoints.
"""

import pytest


@pytest.mark.integration
@pytest.mark.api
class TestHazardCoverageAPI:
    """Test cases for hazard coverage analysis API."""

    def test_get_hazard_coverage_full(self, api_client, clean_database):
        """Test hazard coverage with full traceability chain."""
        # Create complete chain
        api_client.post("/import/hara", json={
            "hazards": [{"id": "H-001", "description": "Test", "asil": "D"}],
            "scenarios": [],
            "safety_goals": [{"id": "SG-001", "description": "Test", "asil": "D"}],
            "relationships": {"MITIGATED_BY": [["H-001", "SG-001"]]}
        })

        api_client.post("/import/requirements", json={
            "fsrs": [{"id": "FSR-001", "text": "Test", "asil": "D", "status": "approved"}],
            "tsrs": [{"id": "TSR-001", "text": "Test", "asil": "D", "status": "approved",
                     "verification_method": "Test"}],
            "components": [],
            "relationships": {
                "REFINED_TO": [["SG-001", "FSR-001"], ["FSR-001", "TSR-001"]]
            }
        })

        api_client.post("/import/tests", json={
            "test_cases": [{"id": "TC-001", "name": "Test", "test_type": "unit", "status": "passed"}],
            "relationships": {"VERIFIED_BY": [["TSR-001", "TC-001"]]}
        })

        # Get coverage
        response = api_client.get("/analytics/coverage/hazard/H-001")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["coverage"]["coverage_status"] == "full"

    def test_get_hazard_coverage_partial(self, api_client, clean_database):
        """Test hazard coverage with partial traceability (no tests)."""
        # Create partial chain (no tests)
        api_client.post("/import/hara", json={
            "hazards": [{"id": "H-001", "description": "Test", "asil": "D"}],
            "scenarios": [],
            "safety_goals": [{"id": "SG-001", "description": "Test", "asil": "D"}],
            "relationships": {"MITIGATED_BY": [["H-001", "SG-001"]]}
        })

        # Get coverage
        response = api_client.get("/analytics/coverage/hazard/H-001")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["coverage"]["coverage_status"] in ["partial", "none"]

    def test_get_hazard_coverage_not_found(self, api_client, clean_database):
        """Test hazard coverage for non-existent hazard."""
        response = api_client.get("/analytics/coverage/hazard/H-NOTFOUND")

        assert response.status_code == 404

    def test_get_all_hazards_coverage(self, api_client, clean_database):
        """Test getting coverage for all hazards."""
        # Create multiple hazards with different coverage
        api_client.post("/import/hara", json={
            "hazards": [
                {"id": "H-001", "description": "Covered", "asil": "D"},
                {"id": "H-002", "description": "Not covered", "asil": "C"}
            ],
            "scenarios": [],
            "safety_goals": [{"id": "SG-001", "description": "Test", "asil": "D"}],
            "relationships": {"MITIGATED_BY": [["H-001", "SG-001"]]}
        })

        response = api_client.get("/analytics/coverage/hazards")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data["data"]
        assert data["data"]["summary"]["total_hazards"] == 2

    def test_get_all_hazards_coverage_asil_filter(self, api_client, clean_database):
        """Test getting coverage with ASIL filter."""
        # Create hazards with different ASIL levels
        api_client.post("/import/hara", json={
            "hazards": [
                {"id": "H-D", "description": "ASIL D", "asil": "D"},
                {"id": "H-C", "description": "ASIL C", "asil": "C"},
                {"id": "H-A", "description": "ASIL A", "asil": "A"}
            ],
            "scenarios": [],
            "safety_goals": [],
            "relationships": {}
        })

        # Filter for ASIL D and C only
        response = api_client.get("/analytics/coverage/hazards?asil=D&asil=C")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["summary"]["total_hazards"] == 2

    def test_get_coverage_statistics(self, api_client, clean_database):
        """Test getting coverage statistics."""
        # Create some hazards
        api_client.post("/import/hara", json={
            "hazards": [
                {"id": "H-001", "description": "Test1", "asil": "D"},
                {"id": "H-002", "description": "Test2", "asil": "C"}
            ],
            "scenarios": [],
            "safety_goals": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/coverage/statistics")

        assert response.status_code == 200
        data = response.json()
        assert "total_hazards" in data
        assert data["total_hazards"] == 2


@pytest.mark.integration
@pytest.mark.api
class TestComponentImpactAPI:
    """Test cases for component impact analysis API."""

    def test_get_component_impact(self, api_client, clean_database):
        """Test component impact analysis."""
        # Create component with some connections
        api_client.post("/import/fmea", json={
            "components": [{"id": "C-001", "name": "Test", "component_type": "hardware"}],
            "failure_modes": [{"id": "FM-001", "description": "Test", "category": "electrical"}],
            "fmea_entries": [],
            "relationships": {"HAS_FAILURE_MODE": [["C-001", "FM-001"]]}
        })

        response = api_client.get("/analytics/impact/component/C-001")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "impact" in data["data"]
        assert "impact_score" in data["data"]["impact"]

    def test_get_component_impact_not_found(self, api_client, clean_database):
        """Test component impact for non-existent component."""
        response = api_client.get("/analytics/impact/component/C-NOTFOUND")

        assert response.status_code == 404

    def test_get_all_components_impact(self, api_client, clean_database):
        """Test getting impact for all components."""
        # Create multiple components
        api_client.post("/import/fmea", json={
            "components": [
                {"id": "C-001", "name": "Component 1", "component_type": "hardware"},
                {"id": "C-002", "name": "Component 2", "component_type": "software"}
            ],
            "failure_modes": [],
            "fmea_entries": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/impact/components")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "components" in data["data"]
        assert len(data["data"]["components"]) == 2

    def test_get_all_components_impact_with_limit(self, api_client, clean_database):
        """Test getting impact with limit parameter."""
        # Create multiple components
        components = [
            {"id": f"C-{i:03d}", "name": f"Component {i}", "component_type": "hardware"}
            for i in range(1, 11)
        ]
        api_client.post("/import/fmea", json={
            "components": components,
            "failure_modes": [],
            "fmea_entries": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/impact/components?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["components"]) == 5

    def test_get_all_components_impact_type_filter(self, api_client, clean_database):
        """Test getting impact with component type filter."""
        api_client.post("/import/fmea", json={
            "components": [
                {"id": "C-HW", "name": "Hardware", "component_type": "hardware"},
                {"id": "C-SW", "name": "Software", "component_type": "software"}
            ],
            "failure_modes": [],
            "fmea_entries": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/impact/components?component_type=hardware")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["components"]) == 1
        assert data["data"]["components"][0]["component_type"] == "hardware"


@pytest.mark.integration
@pytest.mark.api
class TestTraceabilityAPI:
    """Test cases for traceability analysis API."""

    def test_get_traceability_chain(self, api_client, clean_database):
        """Test getting traceability chain for hazard."""
        # Create complete chain
        api_client.post("/import/hara", json={
            "hazards": [{"id": "H-001", "description": "Test", "asil": "D"}],
            "scenarios": [],
            "safety_goals": [{"id": "SG-001", "description": "Test", "asil": "D"}],
            "relationships": {"MITIGATED_BY": [["H-001", "SG-001"]]}
        })

        api_client.post("/import/requirements", json={
            "fsrs": [{"id": "FSR-001", "text": "Test", "asil": "D", "status": "approved"}],
            "tsrs": [{"id": "TSR-001", "text": "Test", "asil": "D", "status": "approved",
                     "verification_method": "Test"}],
            "components": [],
            "relationships": {
                "REFINED_TO": [["SG-001", "FSR-001"], ["FSR-001", "TSR-001"]]
            }
        })

        api_client.post("/import/tests", json={
            "test_cases": [{"id": "TC-001", "name": "Test", "test_type": "unit", "status": "passed"}],
            "relationships": {"VERIFIED_BY": [["TSR-001", "TC-001"]]}
        })

        response = api_client.get("/analytics/traceability/hazard/H-001")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_requirement_traceability(self, api_client, clean_database):
        """Test getting requirement traceability."""
        # Create requirement with upstream/downstream links
        api_client.post("/import/hara", json={
            "hazards": [],
            "scenarios": [],
            "safety_goals": [{"id": "SG-001", "description": "Test", "asil": "D"}],
            "relationships": {}
        })

        api_client.post("/import/requirements", json={
            "fsrs": [{"id": "FSR-001", "text": "Test", "asil": "D", "status": "approved"}],
            "tsrs": [{"id": "TSR-001", "text": "Test", "asil": "D", "status": "approved",
                     "verification_method": "Test"}],
            "components": [],
            "relationships": {
                "REFINED_TO": [["SG-001", "FSR-001"], ["FSR-001", "TSR-001"]]
            }
        })

        response = api_client.get("/analytics/traceability/requirement/FSR-001")

        assert response.status_code == 200
        data = response.json()
        assert "requirement" in data


@pytest.mark.integration
@pytest.mark.api
class TestStatisticsAPI:
    """Test cases for statistics API."""

    def test_get_database_statistics(self, api_client, clean_database):
        """Test getting database statistics."""
        # Create some data
        api_client.post("/import/hara", json={
            "hazards": [{"id": "H-001", "description": "Test", "asil": "D"}],
            "scenarios": [],
            "safety_goals": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/statistics")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data["data"]
        assert "node_counts" in data["data"]

    def test_get_statistics_empty_database(self, api_client, clean_database):
        """Test statistics with empty database."""
        response = api_client.get("/analytics/statistics")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


@pytest.mark.integration
@pytest.mark.api
class TestSearchAndFilterAPI:
    """Test cases for search and filter API."""

    def test_search_hazards(self, api_client, clean_database):
        """Test searching hazards by text."""
        api_client.post("/import/hara", json={
            "hazards": [
                {"id": "H-001", "description": "Unintended acceleration", "asil": "D"},
                {"id": "H-002", "description": "Loss of braking", "asil": "D"},
                {"id": "H-003", "description": "Steering failure", "asil": "C"}
            ],
            "scenarios": [],
            "safety_goals": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/search/hazards?q=acceleration")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["count"] >= 1

    def test_search_components(self, api_client, clean_database):
        """Test searching components by text."""
        api_client.post("/import/fmea", json={
            "components": [
                {"id": "C-001", "name": "Inverter Module", "component_type": "hardware"},
                {"id": "C-002", "name": "Control Software", "component_type": "software"}
            ],
            "failure_modes": [],
            "fmea_entries": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/search/components?q=Inverter")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["count"] >= 1

    def test_filter_hazards_by_asil(self, api_client, clean_database):
        """Test filtering hazards by ASIL level."""
        api_client.post("/import/hara", json={
            "hazards": [
                {"id": "H-D1", "description": "ASIL D hazard 1", "asil": "D"},
                {"id": "H-D2", "description": "ASIL D hazard 2", "asil": "D"},
                {"id": "H-C", "description": "ASIL C hazard", "asil": "C"},
                {"id": "H-A", "description": "ASIL A hazard", "asil": "A"}
            ],
            "scenarios": [],
            "safety_goals": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/filter/hazards?asil=D")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["count"] == 2

    def test_search_with_limit(self, api_client, clean_database):
        """Test search with limit parameter."""
        # Create many hazards
        hazards = [
            {"id": f"H-{i:03d}", "description": f"Test hazard {i}", "asil": "D"}
            for i in range(1, 51)
        ]
        api_client.post("/import/hara", json={
            "hazards": hazards,
            "scenarios": [],
            "safety_goals": [],
            "relationships": {}
        })

        response = api_client.get("/analytics/search/hazards?q=Test&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 10
