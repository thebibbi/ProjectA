"""
Neo4j database driver and connection management.

Provides singleton database driver with connection pooling, health checks,
and session management utilities.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from neo4j import Driver, GraphDatabase, ManagedTransaction, Result, Session
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class Neo4jDriver:
    """
    Singleton Neo4j driver manager.

    Manages database connection, connection pooling, and provides
    convenient methods for database operations.
    """

    _instance: Optional["Neo4jDriver"] = None
    _driver: Optional[Driver] = None

    def __new__(cls) -> "Neo4jDriver":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize driver (only once due to singleton)."""
        if self._driver is None:
            self._initialize_driver()

    def _initialize_driver(self) -> None:
        """
        Initialize Neo4j driver with connection pooling.

        Raises:
            ServiceUnavailable: If cannot connect to Neo4j
            AuthError: If authentication fails
        """
        settings = get_settings()

        try:
            logger.info(f"Connecting to Neo4j at {settings.neo4j_uri}")

            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_lifetime=settings.neo4j_max_connection_lifetime,
                max_connection_pool_size=settings.neo4j_max_connection_pool_size,
                connection_timeout=settings.neo4j_connection_timeout,
            )

            # Verify connectivity
            self._driver.verify_connectivity()

            logger.info("✓ Successfully connected to Neo4j")

        except ServiceUnavailable as e:
            logger.error(f"✗ Cannot connect to Neo4j at {settings.neo4j_uri}: {e}")
            raise
        except AuthError as e:
            logger.error(f"✗ Authentication failed for user '{settings.neo4j_user}': {e}")
            raise
        except Exception as e:
            logger.error(f"✗ Unexpected error connecting to Neo4j: {e}")
            raise

    def close(self) -> None:
        """Close database driver and all connections."""
        if self._driver:
            logger.info("Closing Neo4j driver")
            self._driver.close()
            self._driver = None
            logger.info("✓ Neo4j driver closed")

    @property
    def driver(self) -> Driver:
        """
        Get the Neo4j driver instance.

        Returns:
            Neo4j driver

        Raises:
            RuntimeError: If driver not initialized
        """
        if self._driver is None:
            raise RuntimeError("Neo4j driver not initialized")
        return self._driver

    @contextmanager
    def get_session(self, database: Optional[str] = None) -> Generator[Session, None, None]:
        """
        Get a database session (context manager).

        Args:
            database: Database name (default: from settings)

        Yields:
            Neo4j session

        Example:
            ```python
            with driver.get_session() as session:
                result = session.run("MATCH (n) RETURN count(n)")
                count = result.single()[0]
            ```
        """
        settings = get_settings()
        db_name = database or settings.neo4j_database

        session = self.driver.session(database=db_name)
        try:
            yield session
        finally:
            session.close()

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results as list of dictionaries.

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name (default: from settings)

        Returns:
            List of result records as dictionaries

        Example:
            ```python
            results = driver.execute_query(
                "MATCH (h:Hazard {asil: $asil}) RETURN h",
                parameters={"asil": "D"}
            )
            ```
        """
        parameters = parameters or {}

        with self.get_session(database=database) as session:
            result = session.run(query, parameters)
            return [dict(record) for record in result]

    def execute_write_transaction(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a write query in a transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name (default: from settings)

        Returns:
            List of result records as dictionaries

        Example:
            ```python
            driver.execute_write_transaction(
                "CREATE (h:Hazard {id: $id, description: $desc})",
                parameters={"id": "H-001", "desc": "Unintended acceleration"}
            )
            ```
        """
        parameters = parameters or {}

        def _write_tx(tx: ManagedTransaction) -> List[Dict[str, Any]]:
            result = tx.run(query, parameters)
            return [dict(record) for record in result]

        with self.get_session(database=database) as session:
            return session.execute_write(_write_tx)

    def execute_read_transaction(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query in a transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name (default: from settings)

        Returns:
            List of result records as dictionaries

        Example:
            ```python
            results = driver.execute_read_transaction(
                "MATCH (h:Hazard) WHERE h.asil = $asil RETURN h",
                parameters={"asil": "D"}
            )
            ```
        """
        parameters = parameters or {}

        def _read_tx(tx: ManagedTransaction) -> List[Dict[str, Any]]:
            result = tx.run(query, parameters)
            return [dict(record) for record in result]

        with self.get_session(database=database) as session:
            return session.execute_read(_read_tx)

    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check.

        Returns:
            Health check result with status and details

        Example:
            ```python
            health = driver.health_check()
            if health["status"] == "healthy":
                print("Database is healthy")
            ```
        """
        try:
            # Simple query to verify connectivity
            with self.get_session() as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]

                if test_value != 1:
                    return {
                        "status": "unhealthy",
                        "message": "Database query returned unexpected result",
                        "details": {"expected": 1, "actual": test_value},
                    }

            # Check driver status
            driver_stats = {
                "status": "healthy",
                "message": "Database connection is healthy",
                "details": {
                    "uri": get_settings().neo4j_uri,
                    "database": get_settings().neo4j_database,
                    "connected": True,
                },
            }

            return driver_stats

        except ServiceUnavailable as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": "Cannot connect to database",
                "details": {"error": str(e)},
            }
        except Neo4jError as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": "Database query error",
                "details": {"error": str(e), "code": e.code},
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": "Unexpected error during health check",
                "details": {"error": str(e)},
            }

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get database schema information.

        Returns:
            Schema information with constraints and indexes

        Example:
            ```python
            schema = driver.get_schema_info()
            print(f"Constraints: {len(schema['constraints'])}")
            print(f"Indexes: {len(schema['indexes'])}")
            ```
        """
        try:
            constraints = self.execute_query("SHOW CONSTRAINTS")
            indexes = self.execute_query("SHOW INDEXES")

            return {
                "constraints": constraints,
                "indexes": indexes,
                "constraint_count": len(constraints),
                "index_count": len(indexes),
            }
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            return {
                "error": str(e),
                "constraints": [],
                "indexes": [],
                "constraint_count": 0,
                "index_count": 0,
            }

    def get_node_counts(self) -> Dict[str, int]:
        """
        Get count of nodes by label.

        Returns:
            Dictionary mapping node labels to counts

        Example:
            ```python
            counts = driver.get_node_counts()
            print(f"Hazards: {counts.get('Hazard', 0)}")
            print(f"Components: {counts.get('Component', 0)}")
            ```
        """
        try:
            # Get all node labels and their counts
            query = """
            CALL db.labels() YIELD label
            CALL {
                WITH label
                MATCH (n)
                WHERE label IN labels(n)
                RETURN count(n) as count
            }
            RETURN label, count
            ORDER BY count DESC
            """

            results = self.execute_query(query)
            return {record["label"]: record["count"] for record in results}

        except Exception as e:
            logger.error(f"Failed to get node counts: {e}")
            return {}

    def get_relationship_counts(self) -> Dict[str, int]:
        """
        Get count of relationships by type.

        Returns:
            Dictionary mapping relationship types to counts

        Example:
            ```python
            counts = driver.get_relationship_counts()
            print(f"MITIGATED_BY: {counts.get('MITIGATED_BY', 0)}")
            ```
        """
        try:
            query = """
            CALL db.relationshipTypes() YIELD relationshipType
            CALL {
                WITH relationshipType
                MATCH ()-[r]->()
                WHERE type(r) = relationshipType
                RETURN count(r) as count
            }
            RETURN relationshipType, count
            ORDER BY count DESC
            """

            results = self.execute_query(query)
            return {record["relationshipType"]: record["count"] for record in results}

        except Exception as e:
            logger.error(f"Failed to get relationship counts: {e}")
            return {}


# Singleton instance
_neo4j_driver: Optional[Neo4jDriver] = None


def get_neo4j_driver() -> Neo4jDriver:
    """
    Get singleton Neo4j driver instance.

    Returns:
        Neo4j driver instance

    This function should be used throughout the application to access
    the database driver.
    """
    global _neo4j_driver
    if _neo4j_driver is None:
        _neo4j_driver = Neo4jDriver()
    return _neo4j_driver


def close_neo4j_driver() -> None:
    """
    Close the global Neo4j driver instance.

    Should be called during application shutdown.
    """
    global _neo4j_driver
    if _neo4j_driver is not None:
        _neo4j_driver.close()
        _neo4j_driver = None
