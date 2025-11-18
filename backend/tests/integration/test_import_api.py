"""
Integration tests for import API endpoints.
"""

import pytest


@pytest.mark.integration
@pytest.mark.api
class TestHARAImportAPI:
    """Test cases for HARA import API endpoint."""

    def test_import_hara_success(self, api_client, clean_database, sample_hara_import):
        """Test successful HARA import via API."""
        response = api_client.post("/import/hara", json=sample_hara_import)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["hazards_created"] == 2
        assert data["data"]["scenarios_created"] == 1
        assert data["data"]["safety_goals_created"] == 1
        assert data["data"]["relationships_created"] == 2

    def test_import_hara_validation_error(self, api_client, clean_database):
        """Test HARA import with invalid data."""
        invalid_data = {
            "hazards": [
                {
                    "id": "INVALID_ID",  # Invalid pattern
                    "description": "Test",
                    "asil": "Z"  # Invalid ASIL
                }
            ],
            "scenarios": [],
            "safety_goals": [],
            "relationships": {}
        }

        response = api_client.post("/import/hara", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_import_hara_empty_data(self, api_client, clean_database):
        """Test HARA import with empty dataset."""
        empty_data = {
            "hazards": [],
            "scenarios": [],
            "safety_goals": [],
            "relationships": {}
        }

        response = api_client.post("/import/hara", json=empty_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["hazards_created"] == 0


@pytest.mark.integration
@pytest.mark.api
class TestFMEAImportAPI:
    """Test cases for FMEA import API endpoint."""

    def test_import_fmea_success(self, api_client, clean_database, sample_fmea_import):
        """Test successful FMEA import via API."""
        response = api_client.post("/import/fmea", json=sample_fmea_import)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["components_created"] == 1
        assert data["data"]["failure_modes_created"] == 1
        assert data["data"]["fmea_entries_created"] == 1
        assert data["data"]["relationships_created"] == 2

    def test_import_fmea_duplicate_component(self, api_client, clean_database, sample_fmea_import):
        """Test FMEA import with duplicate component (should skip)."""
        # First import
        response1 = api_client.post("/import/fmea", json=sample_fmea_import)
        assert response1.status_code == 201

        # Second import with same component
        response2 = api_client.post("/import/fmea", json=sample_fmea_import)
        assert response2.status_code == 201

        # Component should be skipped on second import
        data2 = response2.json()
        assert data2["data"]["components_created"] == 0  # Skipped

    def test_import_fmea_rpn_validation(self, api_client, clean_database):
        """Test FMEA import with invalid RPN."""
        invalid_data = {
            "components": [],
            "failure_modes": [],
            "fmea_entries": [
                {
                    "id": "FMEA-TEST-001",
                    "function_description": "Test",
                    "potential_failure": "Failure",
                    "severity": 10,
                    "occurrence": 10,
                    "detection": 10,
                    "rpn": 1500  # Invalid: > 1000
                }
            ],
            "relationships": {}
        }

        response = api_client.post("/import/fmea", json=invalid_data)

        assert response.status_code == 422  # Validation error


@pytest.mark.integration
@pytest.mark.api
class TestRequirementsImportAPI:
    """Test cases for Requirements import API endpoint."""

    def test_import_requirements_success(self, api_client, clean_database):
        """Test successful requirements import via API."""
        # First create safety goal for relationship
        hara_data = {
            "hazards": [],
            "scenarios": [],
            "safety_goals": [
                {
                    "id": "SG-TEST-001",
                    "description": "Test safety goal",
                    "asil": "D"
                }
            ],
            "relationships": {}
        }
        api_client.post("/import/hara", json=hara_data)

        # Now import requirements
        req_data = {
            "fsrs": [
                {
                    "id": "FSR-TEST-001",
                    "text": "Test FSR",
                    "asil": "D",
                    "status": "approved"
                }
            ],
            "tsrs": [
                {
                    "id": "TSR-TEST-001",
                    "text": "Test TSR",
                    "asil": "D",
                    "status": "approved",
                    "verification_method": "Unit test"
                }
            ],
            "components": [],
            "relationships": {
                "REFINED_TO": [
                    ["SG-TEST-001", "FSR-TEST-001"],
                    ["FSR-TEST-001", "TSR-TEST-001"]
                ]
            }
        }

        response = api_client.post("/import/requirements", json=req_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["fsrs_created"] == 1
        assert data["data"]["tsrs_created"] == 1
        assert data["data"]["relationships_created"] == 2


@pytest.mark.integration
@pytest.mark.api
class TestTestsImportAPI:
    """Test cases for Tests import API endpoint."""

    def test_import_tests_success(self, api_client, clean_database):
        """Test successful test cases import via API."""
        # First create TSR for relationship
        req_data = {
            "fsrs": [],
            "tsrs": [
                {
                    "id": "TSR-TEST-001",
                    "text": "Test TSR",
                    "asil": "D",
                    "status": "approved",
                    "verification_method": "Unit test"
                }
            ],
            "components": [],
            "relationships": {}
        }
        api_client.post("/import/requirements", json=req_data)

        # Now import test cases
        test_data = {
            "test_cases": [
                {
                    "id": "TC-TEST-001",
                    "name": "Test case 1",
                    "test_type": "unit",
                    "status": "passed"
                }
            ],
            "relationships": {
                "VERIFIED_BY": [["TSR-TEST-001", "TC-TEST-001"]]
            }
        }

        response = api_client.post("/import/tests", json=test_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["test_cases_created"] == 1
        assert data["data"]["relationships_created"] == 1

    def test_import_tests_various_statuses(self, api_client, clean_database):
        """Test importing test cases with different statuses."""
        test_data = {
            "test_cases": [
                {
                    "id": "TC-PASSED",
                    "name": "Passed test",
                    "test_type": "unit",
                    "status": "passed"
                },
                {
                    "id": "TC-FAILED",
                    "name": "Failed test",
                    "test_type": "unit",
                    "status": "failed"
                },
                {
                    "id": "TC-BLOCKED",
                    "name": "Blocked test",
                    "test_type": "unit",
                    "status": "blocked"
                },
                {
                    "id": "TC-NOTRUN",
                    "name": "Not run test",
                    "test_type": "unit",
                    "status": "not_run"
                }
            ],
            "relationships": {}
        }

        response = api_client.post("/import/tests", json=test_data)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["test_cases_created"] == 4


@pytest.mark.integration
@pytest.mark.api
class TestDefectsImportAPI:
    """Test cases for Defects import API endpoint (Phase 3)."""

    def test_import_defects_success(self, api_client, clean_database):
        """Test successful defects import via API."""
        # First create component
        fmea_data = {
            "components": [
                {
                    "id": "C-TEST-001",
                    "name": "Test Component",
                    "component_type": "hardware"
                }
            ],
            "failure_modes": [],
            "fmea_entries": [],
            "relationships": {}
        }
        api_client.post("/import/fmea", json=fmea_data)

        # Now import defects
        defect_data = {
            "defects": [
                {
                    "id": "D-TEST-001",
                    "title": "Test defect",
                    "description": "Test defect description",
                    "severity": "high",
                    "status": "open",
                    "source": "testing"
                }
            ],
            "relationships": {
                "FOUND_IN": [["D-TEST-001", "C-TEST-001"]]
            }
        }

        response = api_client.post("/import/defects", json=defect_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["defects_created"] == 1
        assert data["data"]["relationships_created"] == 1


@pytest.mark.integration
@pytest.mark.api
class TestCompleteTraceabilityChain:
    """Test complete traceability chain import."""

    def test_import_complete_chain(self, api_client, clean_database):
        """Test importing complete traceability chain from hazard to test."""
        # 1. Import HARA
        hara_response = api_client.post("/import/hara", json={
            "hazards": [
                {"id": "H-001", "description": "Test hazard", "asil": "D"}
            ],
            "scenarios": [],
            "safety_goals": [
                {"id": "SG-001", "description": "Test safety goal", "asil": "D"}
            ],
            "relationships": {
                "MITIGATED_BY": [["H-001", "SG-001"]]
            }
        })
        assert hara_response.status_code == 201

        # 2. Import Requirements
        req_response = api_client.post("/import/requirements", json={
            "fsrs": [
                {"id": "FSR-001", "text": "Test FSR", "asil": "D", "status": "approved"}
            ],
            "tsrs": [
                {"id": "TSR-001", "text": "Test TSR", "asil": "D", "status": "approved",
                 "verification_method": "Test"}
            ],
            "components": [],
            "relationships": {
                "REFINED_TO": [
                    ["SG-001", "FSR-001"],
                    ["FSR-001", "TSR-001"]
                ]
            }
        })
        assert req_response.status_code == 201

        # 3. Import Tests
        test_response = api_client.post("/import/tests", json={
            "test_cases": [
                {"id": "TC-001", "name": "Test case", "test_type": "unit", "status": "passed"}
            ],
            "relationships": {
                "VERIFIED_BY": [["TSR-001", "TC-001"]]
            }
        })
        assert test_response.status_code == 201

        # 4. Verify complete chain exists
        coverage_response = api_client.get("/analytics/coverage/hazard/H-001")
        assert coverage_response.status_code == 200

        coverage_data = coverage_response.json()
        assert coverage_data["data"]["coverage"]["coverage_status"] == "full"
