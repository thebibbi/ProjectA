"""
Requirements import service.

Handles importing FSRs, TSRs, and their relationships.
"""

import logging
from typing import Dict, Any

from app.db import queries
from app.models.schemas import RequirementsImportRequest, RequirementsImportResponse
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class RequirementsImportService(BaseService):
    """
    Service for importing requirements into the knowledge graph.

    Imports:
    - Functional Safety Requirements (FSRs)
    - Technical Safety Requirements (TSRs)
    - Relationships: REFINED_TO, ALLOCATED_TO
    """

    def import_requirements(
        self,
        request: RequirementsImportRequest
    ) -> RequirementsImportResponse:
        """
        Import complete requirements dataset.

        Args:
            request: Requirements import request with FSRs, TSRs, relationships

        Returns:
            RequirementsImportResponse with import statistics

        Raises:
            ValueError: If validation fails
            Exception: If import fails
        """
        self.logger.info("Starting requirements import...")

        try:
            # Statistics counters
            stats = {
                "fsrs_created": 0,
                "tsrs_created": 0,
                "components_created": 0,
                "relationships_created": 0,
            }

            # Import FSRs
            if request.fsrs:
                stats["fsrs_created"] = self._import_fsrs(request.fsrs)

            # Import TSRs
            if request.tsrs:
                stats["tsrs_created"] = self._import_tsrs(request.tsrs)

            # Import components (if provided and not already present)
            if request.components:
                stats["components_created"] = self._import_components(request.components)

            # Import relationships
            if request.relationships:
                stats["relationships_created"] = self._import_relationships(
                    request.relationships
                )

            self.logger.info(f"Requirements import completed: {stats}")

            return RequirementsImportResponse(
                status="success",
                message="Requirements imported successfully",
                data=stats
            )

        except Exception as e:
            self.logger.error(f"Requirements import failed: {e}")
            raise

    def _import_fsrs(self, fsrs: list) -> int:
        """
        Import Functional Safety Requirements.

        Args:
            fsrs: List of FunctionalSafetyRequirementNode models

        Returns:
            Number of FSRs created
        """
        self.logger.info(f"Importing {len(fsrs)} FSR(s)...")

        created_count = 0
        for fsr in fsrs:
            try:
                fsr_data = fsr.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_FSR,
                    fsr_data,
                    "FunctionalSafetyRequirement"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import FSR {fsr.id}: {e}")
                # Continue with next FSR

        self.logger.info(f"Successfully imported {created_count}/{len(fsrs)} FSR(s)")
        return created_count

    def _import_tsrs(self, tsrs: list) -> int:
        """
        Import Technical Safety Requirements.

        Args:
            tsrs: List of TechnicalSafetyRequirementNode models

        Returns:
            Number of TSRs created
        """
        self.logger.info(f"Importing {len(tsrs)} TSR(s)...")

        created_count = 0
        for tsr in tsrs:
            try:
                tsr_data = tsr.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_TSR,
                    tsr_data,
                    "TechnicalSafetyRequirement"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import TSR {tsr.id}: {e}")
                # Continue with next TSR

        self.logger.info(f"Successfully imported {created_count}/{len(tsrs)} TSR(s)")
        return created_count

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

    def _import_relationships(self, relationships: Dict[str, Any]) -> int:
        """
        Import relationships between requirements and other entities.

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
