"""
HARA (Hazard Analysis and Risk Assessment) import service.

Handles importing hazards, scenarios, safety goals, and their relationships.
"""

import logging
from typing import Dict, Any

from app.db import queries
from app.models.schemas import HARAImportRequest, HARAImportResponse
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class HARAImportService(BaseService):
    """
    Service for importing HARA data into the knowledge graph.

    Imports:
    - Hazards with ASIL ratings
    - Operating scenarios
    - Safety goals
    - Relationships: OCCURS_IN, MITIGATED_BY
    """

    def import_hara(self, request: HARAImportRequest) -> HARAImportResponse:
        """
        Import complete HARA dataset.

        Args:
            request: HARA import request with hazards, scenarios, safety goals

        Returns:
            HARAImportResponse with import statistics

        Raises:
            ValueError: If validation fails
            Exception: If import fails
        """
        self.logger.info("Starting HARA import...")

        try:
            # Statistics counters
            stats = {
                "hazards_created": 0,
                "scenarios_created": 0,
                "safety_goals_created": 0,
                "relationships_created": 0,
            }

            # Import hazards
            if request.hazards:
                stats["hazards_created"] = self._import_hazards(request.hazards)

            # Import scenarios
            if request.scenarios:
                stats["scenarios_created"] = self._import_scenarios(request.scenarios)

            # Import safety goals
            if request.safety_goals:
                stats["safety_goals_created"] = self._import_safety_goals(request.safety_goals)

            # Import relationships
            if request.relationships:
                stats["relationships_created"] = self._import_relationships(
                    request.relationships
                )

            self.logger.info(f"HARA import completed: {stats}")

            return HARAImportResponse(
                status="success",
                message="HARA data imported successfully",
                data=stats
            )

        except Exception as e:
            self.logger.error(f"HARA import failed: {e}")
            raise

    def _import_hazards(self, hazards: list) -> int:
        """
        Import hazards.

        Args:
            hazards: List of HazardNode models

        Returns:
            Number of hazards created
        """
        self.logger.info(f"Importing {len(hazards)} hazard(s)...")

        created_count = 0
        for hazard in hazards:
            try:
                hazard_data = hazard.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_HAZARD,
                    hazard_data,
                    "Hazard"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import hazard {hazard.id}: {e}")
                # Continue with next hazard

        self.logger.info(f"Successfully imported {created_count}/{len(hazards)} hazard(s)")
        return created_count

    def _import_scenarios(self, scenarios: list) -> int:
        """
        Import operating scenarios.

        Args:
            scenarios: List of ScenarioNode models

        Returns:
            Number of scenarios created
        """
        self.logger.info(f"Importing {len(scenarios)} scenario(s)...")

        created_count = 0
        for scenario in scenarios:
            try:
                scenario_data = scenario.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_SCENARIO,
                    scenario_data,
                    "Scenario"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import scenario {scenario.id}: {e}")
                # Continue with next scenario

        self.logger.info(f"Successfully imported {created_count}/{len(scenarios)} scenario(s)")
        return created_count

    def _import_safety_goals(self, safety_goals: list) -> int:
        """
        Import safety goals.

        Args:
            safety_goals: List of SafetyGoalNode models

        Returns:
            Number of safety goals created
        """
        self.logger.info(f"Importing {len(safety_goals)} safety goal(s)...")

        created_count = 0
        for sg in safety_goals:
            try:
                sg_data = sg.model_dump(exclude_none=True)
                self._create_node(
                    queries.CREATE_SAFETY_GOAL,
                    sg_data,
                    "SafetyGoal"
                )
                created_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to import safety goal {sg.id}: {e}")
                # Continue with next safety goal

        self.logger.info(f"Successfully imported {created_count}/{len(safety_goals)} safety goal(s)")
        return created_count

    def _import_relationships(self, relationships: Dict[str, Any]) -> int:
        """
        Import relationships between HARA entities.

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
