"""
Tests import service.

Handles importing test cases and their verification relationships.
"""

import logging
from typing import Dict, Any

from app.db import queries
from app.models.schemas import TestsImportRequest, TestsImportResponse
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class TestsImportService(BaseService):
    """
    Service for importing test cases into the knowledge graph.

    Imports:
    - Test cases with status and coverage information
    - Relationships: VERIFIED_BY (TSR -> TestCase, Component -> TestCase)
    """

    def import_tests(self, request: TestsImportRequest) -> TestsImportResponse:
        """
        Import complete test dataset.

        Args:
            request: Tests import request with test cases and relationships

        Returns:
            TestsImportResponse with import statistics

        Raises:
            ValueError: If validation fails
            Exception: If import fails
        """
        self.logger.info("Starting tests import...")

        try:
            # Statistics counters
            stats = {
                "test_cases_created": 0,
                "relationships_created": 0,
            }

            # Import test cases
            if request.test_cases:
                stats["test_cases_created"] = self._import_test_cases(request.test_cases)

            # Import relationships
            if request.relationships:
                stats["relationships_created"] = self._import_relationships(
                    request.relationships
                )

            self.logger.info(f"Tests import completed: {stats}")

            return TestsImportResponse(
                status="success",
                message="Test cases imported successfully",
                data=stats
            )

        except Exception as e:
            self.logger.error(f"Tests import failed: {e}")
            raise

    def _import_test_cases(self, test_cases: list) -> int:
        """
        Import test cases.

        Args:
            test_cases: List of TestCaseNode models

        Returns:
            Number of test cases created
        """
        self.logger.info(f"Importing {len(test_cases)} test case(s)...")

        created_count = 0
        for tc in test_cases:
            try:
                tc_data = tc.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_TEST_CASE,
                    tc_data,
                    "TestCase"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import test case {tc.id}: {e}")
                # Continue with next test case

        self.logger.info(f"Successfully imported {created_count}/{len(test_cases)} test case(s)")
        return created_count

    def _import_relationships(self, relationships: Dict[str, Any]) -> int:
        """
        Import relationships between test cases and requirements/components.

        Args:
            relationships: Dictionary mapping relationship types to [source, target] pairs

        Returns:
            Total number of relationships created
        """
        self.logger.info(f"Importing {len(relationships)} relationship type(s)...")

        total_created = 0

        for rel_type, pairs in relationships.items():
            if not pairs:
                continue

            self.logger.info(f"Creating {len(pairs)} {rel_type} relationship(s)...")

            created_count = 0
            for source_id, target_id in pairs:
                try:
                    self._create_relationship(
                        source_id=source_id,
                        target_id=target_id,
                        rel_type=rel_type
                    )
                    created_count += 1

                except Exception as e:
                    self.logger.warning(
                        f"Failed to create relationship ({source_id})-[{rel_type}]->({target_id}): {e}"
                    )
                    # Continue with next relationship

            self.logger.info(f"Created {created_count}/{len(pairs)} {rel_type} relationship(s)")
            total_created += created_count

        return total_created

    def update_test_status(
        self,
        test_id: str,
        status: str,
        result: str
    ) -> Dict[str, Any]:
        """
        Update test case status and result.

        Args:
            test_id: Test case ID
            status: New status (passed, failed, blocked, etc.)
            result: Test execution result

        Returns:
            Updated test case data

        Raises:
            ValueError: If test case not found
            Exception: If update fails
        """
        self.logger.info(f"Updating test case {test_id} status to {status}")

        try:
            # Check if test exists
            if not self._node_exists(test_id):
                raise ValueError(f"Test case {test_id} not found")

            # Update test status
            result_data = self.driver.execute_write_transaction(
                queries.UPDATE_TEST_STATUS,
                parameters={
                    "test_id": test_id,
                    "status": status,
                    "result": result
                }
            )

            if not result_data:
                raise ValueError(f"Failed to update test case {test_id}")

            self.logger.info(f"Successfully updated test case {test_id}")
            return result_data[0]["tc"]

        except Exception as e:
            self.logger.error(f"Failed to update test case {test_id}: {e}")
            raise
