"""
Defects import service (Phase 3).

Handles importing runtime defects and linking them to components and requirements.
"""

import logging
from typing import Dict, Any

from app.db import queries
from app.models.schemas import DefectsImportRequest, DefectsImportResponse
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class DefectsImportService(BaseService):
    """
    Service for importing defects into the knowledge graph (Phase 3).

    Imports:
    - Defect instances from warranty, field, CV, testing
    - Relationships: FOUND_IN (Defect -> Component), VIOLATES (Defect -> Requirement)
    """

    def import_defects(self, request: DefectsImportRequest) -> DefectsImportResponse:
        """
        Import complete defects dataset.

        Args:
            request: Defects import request with defect instances and relationships

        Returns:
            DefectsImportResponse with import statistics

        Raises:
            ValueError: If validation fails
            Exception: If import fails
        """
        self.logger.info("Starting defects import...")

        try:
            # Statistics counters
            stats = {
                "defects_created": 0,
                "relationships_created": 0,
            }

            # Import defects
            if request.defects:
                stats["defects_created"] = self._import_defects(request.defects)

            # Import relationships
            if request.relationships:
                stats["relationships_created"] = self._import_relationships(
                    request.relationships
                )

            self.logger.info(f"Defects import completed: {stats}")

            return DefectsImportResponse(
                status="success",
                message="Defects imported successfully",
                data=stats
            )

        except Exception as e:
            self.logger.error(f"Defects import failed: {e}")
            raise

    def _import_defects(self, defects: list) -> int:
        """
        Import defect instances.

        Args:
            defects: List of DefectInstanceNode models

        Returns:
            Number of defects created
        """
        self.logger.info(f"Importing {len(defects)} defect(s)...")

        created_count = 0
        for defect in defects:
            try:
                defect_data = defect.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_DEFECT,
                    defect_data,
                    "DefectInstance"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import defect {defect.id}: {e}")
                # Continue with next defect

        self.logger.info(f"Successfully imported {created_count}/{len(defects)} defect(s)")
        return created_count

    def _import_relationships(self, relationships: Dict[str, Any]) -> int:
        """
        Import relationships between defects and components/requirements.

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

    def update_defect_status(
        self,
        defect_id: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update defect status.

        Args:
            defect_id: Defect ID
            status: New status (open, in_progress, resolved, closed, etc.)

        Returns:
            Updated defect data

        Raises:
            ValueError: If defect not found
            Exception: If update fails
        """
        self.logger.info(f"Updating defect {defect_id} status to {status}")

        try:
            # Check if defect exists
            if not self._node_exists(defect_id):
                raise ValueError(f"Defect {defect_id} not found")

            # Update defect status
            result_data = self.driver.execute_write_transaction(
                queries.UPDATE_DEFECT_STATUS,
                parameters={
                    "defect_id": defect_id,
                    "status": status
                }
            )

            if not result_data:
                raise ValueError(f"Failed to update defect {defect_id}")

            self.logger.info(f"Successfully updated defect {defect_id}")
            return result_data[0]["d"]

        except Exception as e:
            self.logger.error(f"Failed to update defect {defect_id}: {e}")
            raise

    def get_defects_by_component(self, component_id: str) -> list:
        """
        Get all defects found in a specific component.

        Args:
            component_id: Component ID

        Returns:
            List of defect data

        Raises:
            ValueError: If component not found
        """
        self.logger.info(f"Getting defects for component {component_id}")

        try:
            # Check if component exists
            if not self._node_exists(component_id):
                raise ValueError(f"Component {component_id} not found")

            # Query defects
            query = """
            MATCH (d:DefectInstance)-[:FOUND_IN]->(c:Component {id: $component_id})
            RETURN d
            ORDER BY d.severity DESC, d.detected_date DESC
            """

            results = self.driver.execute_query(
                query,
                parameters={"component_id": component_id}
            )

            defects = [record["d"] for record in results]
            self.logger.info(f"Found {len(defects)} defect(s) for component {component_id}")

            return defects

        except Exception as e:
            self.logger.error(f"Failed to get defects for component {component_id}: {e}")
            raise
