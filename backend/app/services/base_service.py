"""
Base service class with common functionality.
"""

import logging
from typing import Any, Dict, List, Optional

from app.db.neo4j_driver import Neo4jDriver, get_neo4j_driver
from app.db import queries

logger = logging.getLogger(__name__)


class BaseService:
    """
    Base service class for all import and analytics services.

    Provides common functionality:
    - Database driver access
    - Error handling
    - Logging
    - Statistics tracking
    """

    def __init__(self, driver: Optional[Neo4jDriver] = None):
        """
        Initialize service.

        Args:
            driver: Neo4j driver instance (optional, will use singleton if not provided)
        """
        self.driver = driver or get_neo4j_driver()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _create_node(
        self,
        query: str,
        data: Dict[str, Any],
        node_type: str
    ) -> Dict[str, Any]:
        """
        Create a single node.

        Args:
            query: Cypher query template
            data: Node properties
            node_type: Node type name (for logging)

        Returns:
            Created node data

        Raises:
            Exception: If node creation fails
        """
        try:
            properties = queries.build_node_properties(data)
            result = self.driver.execute_write_transaction(query, properties)

            if not result:
                raise ValueError(f"Failed to create {node_type}: no result returned")

            self.logger.debug(f"Created {node_type}: {data.get('id')}")
            return result[0]

        except Exception as e:
            self.logger.error(f"Failed to create {node_type} {data.get('id')}: {e}")
            raise

    def _create_nodes_batch(
        self,
        nodes_data: List[Dict[str, Any]],
        label: str,
        node_type: str
    ) -> int:
        """
        Create multiple nodes in a batch.

        Args:
            nodes_data: List of node property dictionaries
            label: Neo4j node label
            node_type: Node type name (for logging)

        Returns:
            Number of nodes created

        Raises:
            Exception: If batch creation fails
        """
        if not nodes_data:
            return 0

        try:
            batch_data = queries.build_batch_nodes(nodes_data, label)
            result = self.driver.execute_write_transaction(
                queries.BATCH_CREATE_NODES,
                parameters={"nodes": batch_data}
            )

            count = result[0]["created_count"] if result else 0
            self.logger.info(f"Created {count} {node_type}(s) in batch")
            return count

        except Exception as e:
            self.logger.error(f"Failed to create {node_type} batch: {e}")
            raise

    def _create_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a single relationship.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            rel_type: Relationship type
            properties: Optional relationship properties

        Returns:
            Created relationship data

        Raises:
            Exception: If relationship creation fails
        """
        try:
            params = {
                "source_id": source_id,
                "target_id": target_id,
                "rel_type": rel_type,
                "properties": properties or {}
            }

            result = self.driver.execute_write_transaction(
                queries.CREATE_RELATIONSHIP,
                parameters=params
            )

            self.logger.debug(f"Created relationship: ({source_id})-[{rel_type}]->({target_id})")
            return result[0] if result else {}

        except Exception as e:
            self.logger.error(
                f"Failed to create relationship ({source_id})-[{rel_type}]->({target_id}): {e}"
            )
            raise

    def _create_relationships_batch(
        self,
        relationships: List[tuple[str, str, str, Optional[Dict[str, Any]]]],
        rel_type_name: str
    ) -> int:
        """
        Create multiple relationships in a batch.

        Args:
            relationships: List of (source_id, target_id, rel_type, properties) tuples
            rel_type_name: Relationship type name (for logging)

        Returns:
            Number of relationships created

        Raises:
            Exception: If batch creation fails
        """
        if not relationships:
            return 0

        try:
            batch_data = queries.build_batch_relationships(relationships)
            result = self.driver.execute_write_transaction(
                queries.BATCH_CREATE_RELATIONSHIPS,
                parameters={"relationships": batch_data}
            )

            count = result[0]["created_count"] if result else 0
            self.logger.info(f"Created {count} {rel_type_name} relationship(s) in batch")
            return count

        except Exception as e:
            self.logger.error(f"Failed to create {rel_type_name} relationships batch: {e}")
            raise

    def _node_exists(self, node_id: str) -> bool:
        """
        Check if a node exists.

        Args:
            node_id: Node ID to check

        Returns:
            True if node exists, False otherwise
        """
        try:
            result = self.driver.execute_query(
                "MATCH (n {id: $id}) RETURN count(n) AS count",
                parameters={"id": node_id}
            )
            return result[0]["count"] > 0 if result else False

        except Exception as e:
            self.logger.error(f"Failed to check node existence {node_id}: {e}")
            return False

    def _get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node data or None if not found
        """
        try:
            result = self.driver.execute_query(
                "MATCH (n {id: $id}) RETURN n",
                parameters={"id": node_id}
            )
            return result[0]["n"] if result else None

        except Exception as e:
            self.logger.error(f"Failed to get node {node_id}: {e}")
            return None

    def _build_statistics(
        self,
        **counts: int
    ) -> Dict[str, int]:
        """
        Build statistics dictionary.

        Args:
            **counts: Named count values

        Returns:
            Statistics dictionary
        """
        return {
            **counts,
            "total": sum(counts.values())
        }
