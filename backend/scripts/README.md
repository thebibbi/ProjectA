# Backend Scripts

This directory contains utility scripts for the Safety Graph Twin backend.

## Available Scripts

### `init_schema.py`

Initializes the Neo4j database schema with constraints and indexes.

**Usage:**

```bash
# From backend directory
poetry run python scripts/init_schema.py

# OR from project root
cd backend && poetry run python scripts/init_schema.py

# With Docker
docker-compose exec backend python scripts/init_schema.py
```

**Environment Variables:**

- `NEO4J_URI`: Neo4j connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD`: Neo4j password (default: `safetygraph123`)

**What it does:**

1. Connects to Neo4j database
2. Reads schema definition from `data/schema/neo4j_schema.cypher`
3. Creates all constraints (uniqueness, property existence)
4. Creates all indexes (single-property, composite, full-text)
5. Verifies schema was created successfully
6. Prints summary of constraints and indexes

**Output Example:**

```
======================================================================
Safety Graph Twin - Neo4j Schema Initialization
======================================================================

✓ Connected to Neo4j at bolt://localhost:7687
✓ Reading schema from /path/to/ProjectA/data/schema/neo4j_schema.cypher

⚙ Executing 45 schema statements...
  [1/45] Constraint created
  [2/45] Constraint created
  ...
  [25/45] Index created
  ...

✓ Schema execution complete
  - Constraints: 20 created/updated
  - Indexes: 25 created/updated

⚙ Verifying schema...

======================================================================
SCHEMA VERIFICATION RESULTS
======================================================================

✓ Constraints created: 20
  1. item_id_unique
  2. function_id_unique
  3. component_id_unique
  ...

✓ Indexes created: 25
  1. hazard_asil_idx (RANGE)
  2. component_name_idx (RANGE)
  ...

======================================================================

✅ Schema initialization successful!

✓ Database connection closed
```

**Troubleshooting:**

If initialization fails:

1. **Connection error**: Ensure Neo4j is running (`docker-compose ps neo4j`)
2. **Authentication error**: Check NEO4J_PASSWORD in .env file
3. **File not found**: Run from backend/ directory or ensure data/schema/ exists
4. **Constraint already exists**: Safe to ignore - script handles existing constraints

**When to run:**

- **First time setup**: After starting Neo4j for the first time
- **After schema changes**: When neo4j_schema.cypher is updated
- **After database reset**: If you delete Neo4j data and start fresh

**Safe to re-run:**

Yes! The script uses `CREATE ... IF NOT EXISTS` so it won't fail if constraints/indexes already exist.

---

## Future Scripts

Additional scripts will be added here:

- `import_seed_data.py` - Import example seed data
- `export_graph.py` - Export graph to JSON/GraphML
- `migrate_schema.py` - Schema migration tool
- `validate_data.py` - Data validation and integrity checks
