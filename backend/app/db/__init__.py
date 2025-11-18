"""
Database module for Neo4j connectivity and queries.
"""

from app.db.neo4j_driver import (
    Neo4jDriver,
    get_neo4j_driver,
    close_neo4j_driver,
)

# Import all query templates
from app.db import queries

__all__ = [
    # Driver
    "Neo4jDriver",
    "get_neo4j_driver",
    "close_neo4j_driver",
    # Queries module
    "queries",
]
