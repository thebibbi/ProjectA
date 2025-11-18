"""
Analytics service for knowledge graph queries and analysis.

Provides services for:
- Hazard coverage analysis
- Component impact analysis
- Traceability chains
- Database statistics
"""

import logging
from typing import Dict, Any, List, Optional

from app.db import queries
from app.models.schemas import (
    HazardCoverageResponse,
    ImpactAnalysisResponse,
    StatisticsResponse,
    TraceabilityChain,
    HazardCoverageItem,
    HazardCoverageSummary,
    ImpactedArtifact,
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class AnalyticsService(BaseService):
    """
    Service for knowledge graph analytics and queries.

    Provides methods for:
    - Hazard coverage analysis (single and all hazards)
    - Component impact analysis (single and all components)
    - Traceability chain queries
    - Database statistics and metrics
    """

    # =========================================================================
    # HAZARD COVERAGE ANALYSIS
    # =========================================================================

    def get_hazard_coverage(self, hazard_id: str) -> HazardCoverageResponse:
        """
        Get coverage analysis for a single hazard.

        Traces the path from Hazard → SafetyGoal → FSR → TSR → TestCase
        and determines coverage status (full, partial, none).

        Args:
            hazard_id: Hazard ID to analyze

        Returns:
            HazardCoverageResponse with coverage details

        Raises:
            ValueError: If hazard not found
            Exception: If query fails
        """
        self.logger.info(f"Analyzing coverage for hazard {hazard_id}")

        try:
            # Check if hazard exists
            if not self._node_exists(hazard_id):
                raise ValueError(f"Hazard {hazard_id} not found")

            # Query hazard coverage
            results = self.driver.execute_query(
                queries.GET_HAZARD_COVERAGE,
                parameters={"hazard_id": hazard_id}
            )

            if not results:
                raise ValueError(f"No coverage data found for hazard {hazard_id}")

            coverage_data = results[0]["coverage"]

            # Build response
            return HazardCoverageResponse(
                status="success",
                message=f"Coverage analysis for hazard {hazard_id}",
                data={
                    "hazard_id": hazard_id,
                    "coverage": coverage_data
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to get hazard coverage for {hazard_id}: {e}")
            raise

    def get_all_hazards_coverage(
        self,
        asil_filter: Optional[List[str]] = None
    ) -> HazardCoverageResponse:
        """
        Get coverage analysis for all hazards.

        Args:
            asil_filter: Optional list of ASIL levels to filter (e.g., ["C", "D"])

        Returns:
            HazardCoverageResponse with all hazards coverage

        Raises:
            Exception: If query fails
        """
        self.logger.info("Analyzing coverage for all hazards")

        try:
            # Apply ASIL filter if provided
            if asil_filter:
                query = """
                MATCH (h:Hazard)
                WHERE h.asil IN $asil_levels
                OPTIONAL MATCH (h)-[:MITIGATED_BY]->(sg:SafetyGoal)
                              -[:REFINED_TO]->(fsr:FunctionalSafetyRequirement)
                              -[:REFINED_TO]->(tsr:TechnicalSafetyRequirement)
                              -[:VERIFIED_BY]->(tc:TestCase)
                WITH h,
                     collect(DISTINCT sg.id) AS safety_goals,
                     collect(DISTINCT fsr.id) AS fsrs,
                     collect(DISTINCT tsr.id) AS tsrs,
                     collect(DISTINCT tc.id) AS test_cases,
                     count(DISTINCT tc) AS test_count
                RETURN {
                    hazard_id: h.id,
                    description: h.description,
                    asil: h.asil,
                    safety_goals: safety_goals,
                    fsrs: fsrs,
                    tsrs: tsrs,
                    test_cases: test_cases,
                    coverage_status: CASE
                        WHEN test_count > 0 THEN 'full'
                        WHEN size(safety_goals) > 0 THEN 'partial'
                        ELSE 'none'
                    END
                } AS coverage
                ORDER BY h.asil DESC, h.id
                """
                results = self.driver.execute_query(
                    query,
                    parameters={"asil_levels": asil_filter}
                )
            else:
                results = self.driver.execute_query(queries.GET_ALL_HAZARDS_COVERAGE)

            # Build coverage items
            coverage_items = [record["coverage"] for record in results]

            # Calculate summary statistics
            total = len(coverage_items)
            fully_covered = sum(1 for item in coverage_items if item["coverage_status"] == "full")
            partially_covered = sum(1 for item in coverage_items if item["coverage_status"] == "partial")
            not_covered = sum(1 for item in coverage_items if item["coverage_status"] == "none")

            summary = {
                "total_hazards": total,
                "fully_covered": fully_covered,
                "partially_covered": partially_covered,
                "not_covered": not_covered,
                "coverage_percentage": (fully_covered / total * 100) if total > 0 else 0
            }

            self.logger.info(f"Coverage analysis complete: {summary}")

            return HazardCoverageResponse(
                status="success",
                message=f"Coverage analysis for {total} hazard(s)",
                data={
                    "summary": summary,
                    "hazards": coverage_items
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to get all hazards coverage: {e}")
            raise

    def get_coverage_statistics(self) -> Dict[str, Any]:
        """
        Get overall coverage statistics.

        Returns:
            Coverage statistics with counts and percentages

        Raises:
            Exception: If query fails
        """
        self.logger.info("Getting coverage statistics")

        try:
            results = self.driver.execute_query(queries.GET_COVERAGE_STATISTICS)

            if not results:
                return {
                    "total_hazards": 0,
                    "fully_covered": 0,
                    "partially_covered": 0,
                    "not_covered": 0,
                    "coverage_percentage": 0
                }

            stats = results[0]["statistics"]
            self.logger.info(f"Coverage statistics: {stats}")

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get coverage statistics: {e}")
            raise

    # =========================================================================
    # COMPONENT IMPACT ANALYSIS
    # =========================================================================

    def get_component_impact(self, component_id: str) -> ImpactAnalysisResponse:
        """
        Get impact analysis for a single component.

        Analyzes all artifacts connected to the component:
        - Hazards
        - Safety goals
        - Functions
        - Test cases
        - Failure modes
        - FMEA entries
        - Defects

        Args:
            component_id: Component ID to analyze

        Returns:
            ImpactAnalysisResponse with impact details

        Raises:
            ValueError: If component not found
            Exception: If query fails
        """
        self.logger.info(f"Analyzing impact for component {component_id}")

        try:
            # Check if component exists
            if not self._node_exists(component_id):
                raise ValueError(f"Component {component_id} not found")

            # Query component impact
            results = self.driver.execute_query(
                queries.GET_COMPONENT_IMPACT,
                parameters={"component_id": component_id}
            )

            if not results:
                raise ValueError(f"No impact data found for component {component_id}")

            impact_data = results[0]["impact"]

            # Build response
            return ImpactAnalysisResponse(
                status="success",
                message=f"Impact analysis for component {component_id}",
                data={
                    "component_id": component_id,
                    "impact": impact_data
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to get component impact for {component_id}: {e}")
            raise

    def get_all_components_impact(
        self,
        component_type_filter: Optional[str] = None,
        limit: int = 100
    ) -> ImpactAnalysisResponse:
        """
        Get impact analysis for all components (ranked by impact score).

        Args:
            component_type_filter: Optional component type filter (hardware, software, etc.)
            limit: Maximum number of components to return (default: 100)

        Returns:
            ImpactAnalysisResponse with all components impact

        Raises:
            Exception: If query fails
        """
        self.logger.info(f"Analyzing impact for all components (limit: {limit})")

        try:
            # Apply component type filter if provided
            if component_type_filter:
                query = """
                MATCH (c:Component)
                WHERE c.component_type = $component_type
                OPTIONAL MATCH (c)-[:IMPLEMENTS]->(f:Function)
                              -[:CONTRIBUTES_TO]->(sg:SafetyGoal)
                              <-[:MITIGATED_BY]-(h:Hazard)
                OPTIONAL MATCH (c)-[:HAS_FAILURE_MODE]->(fm:FailureMode)
                WITH c,
                     count(DISTINCT h) AS hazard_count,
                     count(DISTINCT sg) AS safety_goal_count,
                     count(DISTINCT fm) AS failure_mode_count,
                     max(h.asil) AS max_asil
                RETURN {
                    component_id: c.id,
                    name: c.name,
                    component_type: c.component_type,
                    hazard_count: hazard_count,
                    safety_goal_count: safety_goal_count,
                    failure_mode_count: failure_mode_count,
                    max_asil: max_asil,
                    impact_score: hazard_count * 10 + safety_goal_count * 5 + failure_mode_count * 3
                } AS impact
                ORDER BY impact.impact_score DESC
                LIMIT $limit
                """
                results = self.driver.execute_query(
                    query,
                    parameters={"component_type": component_type_filter, "limit": limit}
                )
            else:
                query = queries.GET_ALL_COMPONENTS_IMPACT + f"\nLIMIT {limit}"
                results = self.driver.execute_query(query)

            # Build impact items
            impact_items = [record["impact"] for record in results]

            self.logger.info(f"Impact analysis complete for {len(impact_items)} component(s)")

            return ImpactAnalysisResponse(
                status="success",
                message=f"Impact analysis for {len(impact_items)} component(s)",
                data={
                    "components": impact_items,
                    "total_analyzed": len(impact_items)
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to get all components impact: {e}")
            raise

    # =========================================================================
    # TRACEABILITY ANALYSIS
    # =========================================================================

    def get_traceability_chain(self, hazard_id: str) -> List[TraceabilityChain]:
        """
        Get complete traceability chains for a hazard.

        Returns all complete paths from Hazard → SafetyGoal → FSR → TSR → TestCase.

        Args:
            hazard_id: Hazard ID

        Returns:
            List of traceability chains

        Raises:
            ValueError: If hazard not found
            Exception: If query fails
        """
        self.logger.info(f"Getting traceability chains for hazard {hazard_id}")

        try:
            # Check if hazard exists
            if not self._node_exists(hazard_id):
                raise ValueError(f"Hazard {hazard_id} not found")

            # Query traceability chains
            results = self.driver.execute_query(
                queries.GET_TRACEABILITY_CHAIN,
                parameters={"hazard_id": hazard_id}
            )

            # Build traceability chain objects
            chains = []
            for record in results:
                chain_data = record["chain"]
                chains.append(TraceabilityChain(
                    hazard=chain_data["hazard"],
                    safety_goal=chain_data["safety_goal"],
                    fsr=chain_data["fsr"],
                    tsr=chain_data["tsr"],
                    test_case=chain_data["test_case"]
                ))

            self.logger.info(f"Found {len(chains)} traceability chain(s) for hazard {hazard_id}")

            return chains

        except Exception as e:
            self.logger.error(f"Failed to get traceability chains for {hazard_id}: {e}")
            raise

    def get_requirement_traceability(self, requirement_id: str) -> Dict[str, Any]:
        """
        Get traceability for a requirement (upstream and downstream).

        Args:
            requirement_id: Requirement ID (FSR or TSR)

        Returns:
            Traceability data with upstream and downstream links

        Raises:
            ValueError: If requirement not found
            Exception: If query fails
        """
        self.logger.info(f"Getting traceability for requirement {requirement_id}")

        try:
            # Check if requirement exists
            if not self._node_exists(requirement_id):
                raise ValueError(f"Requirement {requirement_id} not found")

            # Query requirement traceability
            results = self.driver.execute_query(
                queries.GET_REQUIREMENT_TRACEABILITY,
                parameters={"requirement_id": requirement_id}
            )

            if not results:
                raise ValueError(f"No traceability data found for requirement {requirement_id}")

            traceability_data = results[0]["traceability"]

            self.logger.info(f"Got traceability for requirement {requirement_id}")

            return traceability_data

        except Exception as e:
            self.logger.error(f"Failed to get requirement traceability for {requirement_id}: {e}")
            raise

    # =========================================================================
    # STATISTICS AND METRICS
    # =========================================================================

    def get_database_statistics(self) -> StatisticsResponse:
        """
        Get comprehensive database statistics.

        Returns:
            StatisticsResponse with node counts, relationship counts, etc.

        Raises:
            Exception: If query fails
        """
        self.logger.info("Getting database statistics")

        try:
            # Get node counts
            node_stats = self.driver.execute_query(queries.GET_NODE_STATISTICS)
            node_counts = {record["label"]: record["count"] for record in node_stats}

            # Get relationship counts
            rel_stats = self.driver.execute_query(queries.GET_RELATIONSHIP_STATISTICS)
            rel_counts = {record["relationship_type"]: record["count"] for record in rel_stats}

            # Get ASIL distribution
            asil_stats = self.driver.execute_query(queries.GET_ASIL_DISTRIBUTION)
            asil_distribution = {}
            for record in asil_stats:
                node_type = record["node_type"]
                asil = record["asil"]
                count = record["count"]

                if node_type not in asil_distribution:
                    asil_distribution[node_type] = {}

                asil_distribution[node_type][asil] = count

            # Get test status statistics
            test_stats = self.driver.execute_query(queries.GET_TEST_STATUS_STATISTICS)
            test_status_counts = {record["status"]: record["count"] for record in test_stats}

            # Get database summary
            summary_stats = self.driver.execute_query(queries.GET_DATABASE_SUMMARY)
            summary = summary_stats[0]["summary"] if summary_stats else {}

            statistics = {
                "summary": summary,
                "node_counts": node_counts,
                "relationship_counts": rel_counts,
                "asil_distribution": asil_distribution,
                "test_status_counts": test_status_counts
            }

            self.logger.info(f"Database statistics retrieved: {summary}")

            return StatisticsResponse(
                status="success",
                message="Database statistics retrieved",
                data=statistics
            )

        except Exception as e:
            self.logger.error(f"Failed to get database statistics: {e}")
            raise

    def get_node_counts(self) -> Dict[str, int]:
        """
        Get node counts by label.

        Returns:
            Dictionary mapping labels to counts

        Raises:
            Exception: If query fails
        """
        try:
            return self.driver.get_node_counts()
        except Exception as e:
            self.logger.error(f"Failed to get node counts: {e}")
            raise

    def get_relationship_counts(self) -> Dict[str, int]:
        """
        Get relationship counts by type.

        Returns:
            Dictionary mapping relationship types to counts

        Raises:
            Exception: If query fails
        """
        try:
            return self.driver.get_relationship_counts()
        except Exception as e:
            self.logger.error(f"Failed to get relationship counts: {e}")
            raise

    # =========================================================================
    # SEARCH AND FILTER
    # =========================================================================

    def search_hazards(self, search_text: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search hazards by text.

        Args:
            search_text: Search query
            limit: Maximum results (default: 20)

        Returns:
            List of matching hazards

        Raises:
            Exception: If query fails
        """
        self.logger.info(f"Searching hazards for: {search_text}")

        try:
            results = self.driver.execute_query(
                queries.SEARCH_HAZARDS,
                parameters={"search_text": search_text, "limit": limit}
            )

            hazards = [record["h"] for record in results]
            self.logger.info(f"Found {len(hazards)} matching hazard(s)")

            return hazards

        except Exception as e:
            self.logger.error(f"Failed to search hazards: {e}")
            raise

    def search_components(self, search_text: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search components by text.

        Args:
            search_text: Search query
            limit: Maximum results (default: 20)

        Returns:
            List of matching components

        Raises:
            Exception: If query fails
        """
        self.logger.info(f"Searching components for: {search_text}")

        try:
            results = self.driver.execute_query(
                queries.SEARCH_COMPONENTS,
                parameters={"search_text": search_text, "limit": limit}
            )

            components = [record["c"] for record in results]
            self.logger.info(f"Found {len(components)} matching component(s)")

            return components

        except Exception as e:
            self.logger.error(f"Failed to search components: {e}")
            raise

    def filter_hazards_by_asil(self, asil_levels: List[str]) -> List[Dict[str, Any]]:
        """
        Filter hazards by ASIL level.

        Args:
            asil_levels: List of ASIL levels (e.g., ["C", "D"])

        Returns:
            List of filtered hazards

        Raises:
            Exception: If query fails
        """
        self.logger.info(f"Filtering hazards by ASIL: {asil_levels}")

        try:
            results = self.driver.execute_query(
                queries.FILTER_HAZARDS_BY_ASIL,
                parameters={"asil_levels": asil_levels}
            )

            hazards = [record["h"] for record in results]
            self.logger.info(f"Found {len(hazards)} hazard(s) with ASIL in {asil_levels}")

            return hazards

        except Exception as e:
            self.logger.error(f"Failed to filter hazards by ASIL: {e}")
            raise
