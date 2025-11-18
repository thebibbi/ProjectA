"""
FMEA (Failure Mode and Effects Analysis) import service.

Handles importing FMEA entries, failure modes, components, and their relationships.
"""

import logging
from typing import Dict, Any

from app.db import queries
from app.models.schemas import FMEAImportRequest, FMEAImportResponse
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class FMEAImportService(BaseService):
    """
    Service for importing FMEA data into the knowledge graph.

    Imports:
    - FMEA entries with RPN scores
    - Failure modes
    - Components (if not already present)
    - Relationships: HAS_FAILURE_MODE, ANALYZED_IN
    """

    def import_fmea(self, request: FMEAImportRequest) -> FMEAImportResponse:
        """
        Import complete FMEA dataset.

        Args:
            request: FMEA import request with entries, failure modes, components

        Returns:
            FMEAImportResponse with import statistics

        Raises:
            ValueError: If validation fails
            Exception: If import fails
        """
        self.logger.info("Starting FMEA import...")

        try:
            # Statistics counters
            stats = {
                "fmea_entries_created": 0,
                "failure_modes_created": 0,
                "components_created": 0,
                "relationships_created": 0,
            }

            # Import components (if provided)
            if request.components:
                stats["components_created"] = self._import_components(request.components)

            # Import failure modes
            if request.failure_modes:
                stats["failure_modes_created"] = self._import_failure_modes(
                    request.failure_modes
                )

            # Import FMEA entries
            if request.fmea_entries:
                stats["fmea_entries_created"] = self._import_fmea_entries(
                    request.fmea_entries
                )

            # Import relationships
            if request.relationships:
                stats["relationships_created"] = self._import_relationships(
                    request.relationships
                )

            self.logger.info(f"FMEA import completed: {stats}")

            return FMEAImportResponse(
                status="success",
                message="FMEA data imported successfully",
                data=stats
            )

        except Exception as e:
            self.logger.error(f"FMEA import failed: {e}")
            raise

    def _import_components(self, components: list) -> int:
        """
        Import components.

        Args:
            components: List of ComponentNode models

        Returns:
            Number of components created
        """
        self.logger.info(f"Importing {len(components)} component(s)...")

        created_count = 0
        for component in components:
            try:
                # Check if component already exists
                if self._node_exists(component.id):
                    self.logger.debug(f"Component {component.id} already exists, skipping")
                    continue

                component_data = component.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_COMPONENT,
                    component_data,
                    "Component"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import component {component.id}: {e}")
                # Continue with next component

        self.logger.info(f"Successfully imported {created_count}/{len(components)} component(s)")
        return created_count

    def _import_failure_modes(self, failure_modes: list) -> int:
        """
        Import failure modes.

        Args:
            failure_modes: List of FailureModeNode models

        Returns:
            Number of failure modes created
        """
        self.logger.info(f"Importing {len(failure_modes)} failure mode(s)...")

        created_count = 0
        for fm in failure_modes:
            try:
                fm_data = fm.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_FAILURE_MODE,
                    fm_data,
                    "FailureMode"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import failure mode {fm.id}: {e}")
                # Continue with next failure mode

        self.logger.info(f"Successfully imported {created_count}/{len(failure_modes)} failure mode(s)")
        return created_count

    def _import_fmea_entries(self, fmea_entries: list) -> int:
        """
        Import FMEA entries.

        Args:
            fmea_entries: List of FMEAEntryNode models

        Returns:
            Number of FMEA entries created
        """
        self.logger.info(f"Importing {len(fmea_entries)} FMEA entry/entries...")

        created_count = 0
        for entry in fmea_entries:
            try:
                entry_data = entry.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_FMEA_ENTRY,
                    entry_data,
                    "FMEAEntry"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import FMEA entry {entry.id}: {e}")
                # Continue with next entry

        self.logger.info(f"Successfully imported {created_count}/{len(fmea_entries)} FMEA entry/entries")
        return created_count

    def _import_relationships(self, relationships: Dict[str, Any]) -> int:
        """
        Import relationships between FMEA entities.

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
