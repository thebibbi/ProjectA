#!/usr/bin/env python3
"""
Initialize Neo4j database schema for Safety Graph Twin.

This script:
1. Connects to Neo4j database
2. Executes schema definition (constraints and indexes)
3. Verifies schema creation
4. Reports status

Usage:
    python scripts/init_schema.py

Environment variables required:
    NEO4J_URI: Neo4j connection URI (default: bolt://localhost:7687)
    NEO4J_USER: Neo4j username (default: neo4j)
    NEO4J_PASSWORD: Neo4j password (required)
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError


class SchemaInitializer:
    """Initialize Neo4j database schema."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "safetygraph123",
    ):
        """
        Initialize schema initializer.

        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Driver | None = None

    def connect(self) -> bool:
        """
        Connect to Neo4j database.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Verify connectivity
            self.driver.verify_connectivity()
            print(f"✓ Connected to Neo4j at {self.uri}")
            return True
        except ServiceUnavailable:
            print(f"✗ Error: Cannot connect to Neo4j at {self.uri}")
            print("  Make sure Neo4j is running and accessible")
            return False
        except AuthError:
            print(f"✗ Error: Authentication failed for user '{self.user}'")
            print("  Check your credentials")
            return False
        except Exception as e:
            print(f"✗ Error: Unexpected error connecting to Neo4j: {e}")
            return False

    def close(self) -> None:
        """Close database connection."""
        if self.driver:
            self.driver.close()
            print("✓ Database connection closed")

    def read_schema_file(self) -> str:
        """
        Read the schema Cypher file.

        Returns:
            Cypher script content

        Raises:
            FileNotFoundError: If schema file not found
        """
        # Get project root (2 levels up from scripts/)
        project_root = Path(__file__).parent.parent.parent
        schema_file = project_root / "data" / "schema" / "neo4j_schema.cypher"

        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")

        print(f"✓ Reading schema from {schema_file}")
        return schema_file.read_text()

    def execute_schema(self, schema_script: str) -> tuple[int, int]:
        """
        Execute schema creation script.

        Args:
            schema_script: Cypher script content

        Returns:
            Tuple of (constraints_created, indexes_created)
        """
        if not self.driver:
            raise RuntimeError("Not connected to database")

        # Split script into individual statements
        statements = [
            stmt.strip()
            for stmt in schema_script.split(";")
            if stmt.strip()
            and not stmt.strip().startswith("//")
            and "CREATE CONSTRAINT" in stmt or "CREATE INDEX" in stmt or "CREATE FULLTEXT INDEX" in stmt
        ]

        constraints_created = 0
        indexes_created = 0

        print(f"\n⚙ Executing {len(statements)} schema statements...")

        with self.driver.session() as session:
            for i, statement in enumerate(statements, 1):
                try:
                    # Add semicolon back
                    full_statement = statement + ";"
                    session.run(full_statement)

                    if "CONSTRAINT" in statement:
                        constraints_created += 1
                        print(f"  [{i}/{len(statements)}] Constraint created")
                    elif "INDEX" in statement:
                        indexes_created += 1
                        print(f"  [{i}/{len(statements)}] Index created")

                except Exception as e:
                    # Constraint/index might already exist
                    if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                        print(f"  [{i}/{len(statements)}] Already exists (skipped)")
                    else:
                        print(f"  [{i}/{len(statements)}] Error: {e}")

        return constraints_created, indexes_created

    def verify_schema(self) -> Dict[str, List[str]]:
        """
        Verify schema was created successfully.

        Returns:
            Dictionary with lists of constraints and indexes
        """
        if not self.driver:
            raise RuntimeError("Not connected to database")

        result = {"constraints": [], "indexes": []}

        with self.driver.session() as session:
            # Get constraints
            constraints_result = session.run("SHOW CONSTRAINTS")
            for record in constraints_result:
                constraint_name = record.get("name", "unknown")
                result["constraints"].append(constraint_name)

            # Get indexes
            indexes_result = session.run("SHOW INDEXES")
            for record in indexes_result:
                index_name = record.get("name", "unknown")
                index_type = record.get("type", "unknown")
                result["indexes"].append(f"{index_name} ({index_type})")

        return result

    def print_verification_results(self, verification: Dict[str, List[str]]) -> None:
        """
        Print verification results.

        Args:
            verification: Dictionary with constraints and indexes
        """
        print("\n" + "=" * 70)
        print("SCHEMA VERIFICATION RESULTS")
        print("=" * 70)

        print(f"\n✓ Constraints created: {len(verification['constraints'])}")
        if verification["constraints"]:
            for i, constraint in enumerate(verification["constraints"][:10], 1):
                print(f"  {i}. {constraint}")
            if len(verification["constraints"]) > 10:
                print(f"  ... and {len(verification['constraints']) - 10} more")

        print(f"\n✓ Indexes created: {len(verification['indexes'])}")
        if verification["indexes"]:
            for i, index in enumerate(verification["indexes"][:10], 1):
                print(f"  {i}. {index}")
            if len(verification["indexes"]) > 10:
                print(f"  ... and {len(verification['indexes']) - 10} more")

        print("\n" + "=" * 70)

    def run(self) -> bool:
        """
        Run the complete schema initialization process.

        Returns:
            True if successful, False otherwise
        """
        print("=" * 70)
        print("Safety Graph Twin - Neo4j Schema Initialization")
        print("=" * 70)
        print()

        # Connect to database
        if not self.connect():
            return False

        try:
            # Read schema file
            schema_script = self.read_schema_file()

            # Execute schema
            constraints_created, indexes_created = self.execute_schema(schema_script)
            print(f"\n✓ Schema execution complete")
            print(f"  - Constraints: {constraints_created} created/updated")
            print(f"  - Indexes: {indexes_created} created/updated")

            # Verify schema
            print("\n⚙ Verifying schema...")
            verification = self.verify_schema()
            self.print_verification_results(verification)

            print("\n✅ Schema initialization successful!\n")
            return True

        except FileNotFoundError as e:
            print(f"\n✗ Error: {e}")
            return False
        except Exception as e:
            print(f"\n✗ Error during schema initialization: {e}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            self.close()


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Get configuration from environment variables
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "safetygraph123")

    if not neo4j_password and neo4j_password != "safetygraph123":
        print("Error: NEO4J_PASSWORD environment variable not set")
        return 1

    # Initialize schema
    initializer = SchemaInitializer(
        uri=neo4j_uri,
        user=neo4j_user,
        password=neo4j_password,
    )

    success = initializer.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
