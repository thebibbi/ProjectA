# Safety Graph Twin Tests

Comprehensive test suite for the Safety Graph Twin backend API.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── pytest.ini               # Pytest settings (moved to backend/)
├── unit/                    # Unit tests (fast, no external dependencies)
│   ├── __init__.py
│   ├── test_hara_import_service.py
│   └── ...
├── integration/             # Integration tests (requires database)
│   ├── __init__.py
│   ├── test_import_api.py
│   ├── test_analytics_api.py
│   └── ...
└── fixtures/                # Reusable test fixtures
    └── __init__.py
```

## Test Categories

### Unit Tests (`tests/unit/`)

Fast tests with no external dependencies:
- Service layer logic
- Data model validation
- Utility functions
- Business logic

**Markers:** `@pytest.mark.unit`, `@pytest.mark.service`

### Integration Tests (`tests/integration/`)

Tests requiring database and API:
- API endpoint functionality
- Database queries
- Complete workflows
- End-to-end scenarios

**Markers:** `@pytest.mark.integration`, `@pytest.mark.api`, `@pytest.mark.db`

## Running Tests

### Prerequisites

1. **Neo4j Database**: Ensure Neo4j is running
   ```bash
   docker-compose up -d neo4j
   ```

2. **Install Dependencies**:
   ```bash
   cd backend
   poetry install
   ```

### Run All Tests

```bash
poetry run pytest
```

### Run Specific Test Categories

**Unit tests only (fast):**
```bash
poetry run pytest -m unit
```

**Integration tests only:**
```bash
poetry run pytest -m integration
```

**API tests:**
```bash
poetry run pytest -m api
```

**Service tests:**
```bash
poetry run pytest -m service
```

### Run Specific Test Files

```bash
poetry run pytest tests/unit/test_hara_import_service.py
poetry run pytest tests/integration/test_import_api.py
```

### Run Specific Test Functions

```bash
poetry run pytest tests/unit/test_hara_import_service.py::TestHARAImportService::test_import_complete_hara
```

### Run with Coverage

```bash
poetry run pytest --cov=app --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

### Verbose Output

```bash
poetry run pytest -v
poetry run pytest -vv  # Extra verbose
```

### Show Print Statements

```bash
poetry run pytest -s
```

### Stop on First Failure

```bash
poetry run pytest -x
```

### Run Last Failed Tests

```bash
poetry run pytest --lf
```

## Test Fixtures

### Database Fixtures

**`clean_database`**
- Cleans all data from Neo4j before each test
- **WARNING**: Only use with test database!

**`neo4j_driver`**
- Provides Neo4j driver instance
- Automatically includes `clean_database`

**`neo4j_session_driver`**
- Session-scoped driver (reused across tests)

### API Fixtures

**`api_client`**
- FastAPI test client
- No database connection required (uses lifespan events)

### Data Fixtures

**`sample_hazard`**, **`sample_safety_goal`**, **`sample_component`**, etc.
- Pre-configured test data
- Use for quick test setup

**`sample_hara_import`**, **`sample_fmea_import`**
- Complete import request payloads
- Use for API testing

### Factory Fixtures

**`create_test_node(label, properties)`**
- Create nodes in database
- Returns created node

**`create_test_relationship(source_id, target_id, rel_type)`**
- Create relationships in database
- Returns created relationship

## Writing Tests

### Unit Test Example

```python
import pytest
from app.services.hara_import import HARAImportService
from app.models.nodes import HazardNode

@pytest.mark.unit
@pytest.mark.service
class TestMyService:
    """Test cases for my service."""

    def test_something(self, neo4j_driver):
        """Test description."""
        service = HARAImportService(driver=neo4j_driver)

        result = service.do_something()

        assert result is not None
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
@pytest.mark.api
class TestMyAPI:
    """Test cases for my API."""

    def test_endpoint(self, api_client, clean_database):
        """Test description."""
        response = api_client.post("/import/hara", json={...})

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
```

### Using Fixtures

```python
def test_with_sample_data(self, api_client, clean_database, sample_hara_import):
    """Test using sample data fixture."""
    response = api_client.post("/import/hara", json=sample_hara_import)
    assert response.status_code == 201

def test_with_factory(self, create_test_node):
    """Test using factory fixture."""
    node = create_test_node("Hazard", {
        "id": "H-TEST-001",
        "description": "Test hazard",
        "asil": "D"
    })
    assert node["id"] == "H-TEST-001"
```

## Test Coverage

Target coverage goals:
- **Overall**: ≥80%
- **Services**: ≥85%
- **API endpoints**: ≥90%
- **Critical paths**: 100%

View current coverage:
```bash
poetry run pytest --cov=app --cov-report=term-missing
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    poetry install
    poetry run pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Test Database

### Configuration

Tests use the Neo4j database configured in `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=safetygraph123
```

### Database Isolation

Each test using `clean_database` fixture:
1. Deletes all existing data before test
2. Runs test in clean environment
3. (Optionally) Cleans up after test

**IMPORTANT**: Never run tests against production database!

### Parallel Test Execution

Tests can run in parallel with pytest-xdist:

```bash
poetry run pytest -n auto  # Use all CPU cores
poetry run pytest -n 4     # Use 4 workers
```

**Note**: Requires separate test database per worker or test isolation strategy.

## Debugging Tests

### Run Single Test with Debugger

```python
def test_something(self):
    import pdb; pdb.set_trace()  # Breakpoint
    result = do_something()
    assert result is not None
```

### Print Debugging

```bash
poetry run pytest -s  # Show print() statements
```

### Verbose Errors

```bash
poetry run pytest --tb=long  # Full tracebacks
```

## Best Practices

### 1. Test Isolation

✅ **Good**: Each test cleans database
```python
def test_import(self, api_client, clean_database):
    # Database is clean
    response = api_client.post("/import/hara", json=data)
    assert response.status_code == 201
```

❌ **Bad**: Tests depend on each other
```python
def test_import(self, api_client):
    # Assumes data from previous test
    response = api_client.get("/analytics/statistics")
```

### 2. Descriptive Names

✅ **Good**: Describes what is tested
```python
def test_import_hara_with_invalid_asil_fails():
    ...
```

❌ **Bad**: Vague name
```python
def test_import():
    ...
```

### 3. Arrange-Act-Assert Pattern

```python
def test_something(self):
    # Arrange: Set up test data
    data = {"id": "H-001", "description": "Test"}

    # Act: Perform action
    result = service.import_data(data)

    # Assert: Verify outcome
    assert result.status == "success"
```

### 4. Test One Thing

✅ **Good**: Tests single behavior
```python
def test_import_creates_hazard():
    # Test only hazard creation
    ...

def test_import_creates_relationships():
    # Test only relationship creation
    ...
```

❌ **Bad**: Tests multiple things
```python
def test_import():
    # Tests hazard creation, relationships, validation, etc.
    ...
```

### 5. Use Markers

```python
@pytest.mark.slow
@pytest.mark.integration
def test_large_import(self):
    # Long-running integration test
    ...
```

## Troubleshooting

### Database Connection Errors

**Problem**: `ServiceUnavailable: Unable to connect`

**Solution**:
1. Check Neo4j is running: `docker ps`
2. Verify connection settings in `.env`
3. Test connection: `docker exec -it neo4j cypher-shell`

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
1. Ensure working directory is `backend/`
2. Install dependencies: `poetry install`
3. Run tests with poetry: `poetry run pytest`

### Fixture Not Found

**Problem**: `fixture 'clean_database' not found`

**Solution**:
1. Ensure `conftest.py` is in `tests/` directory
2. Check fixture is defined in `conftest.py`
3. Verify test file is in `tests/` subdirectory

### Tests Pass Individually but Fail Together

**Problem**: Test isolation issues

**Solution**:
1. Ensure all tests use `clean_database` fixture
2. Don't rely on test execution order
3. Check for global state modifications

## Performance

### Slow Tests

Optimize slow tests:
1. Use `@pytest.mark.slow` marker
2. Mock external dependencies in unit tests
3. Use smaller datasets
4. Consider parallelization

### Database Performance

Improve test database performance:
1. Use separate test database (not production!)
2. Disable unnecessary indexes during tests
3. Use transactions for bulk operations
4. Consider in-memory Neo4j for unit tests

## Contributing

When adding new tests:
1. Follow existing patterns
2. Use appropriate markers
3. Add docstrings
4. Ensure tests are isolated
5. Aim for >80% coverage
6. Run full test suite before committing

---

**Last Updated**: 2025-11-18
**Version**: 1.0 (M1.10)
