# Safety Graph Twin

A knowledge graph system for ISO 26262 and STPA safety analysis that unifies safety-critical automotive/robotics system documentation to enable impact analysis, coverage tracking, and runtime monitoring.

## 🎯 Overview

Safety Graph Twin breaks down data silos between safety artifacts by creating an interconnected graph database linking:
- System architecture (SysML-style blocks, functions, signals)
- Safety artifacts (HARA, SOTIF, hazards, ASIL ratings)
- Safety analyses (FMEA, FTA, FMEDA, STPA)
- Requirements and test cases with full traceability
- Field defects and runtime events

### Key Capabilities

- **Impact Analysis**: Answer "what breaks if X changes?" in seconds instead of days
- **Coverage Analysis**: Identify untested hazards and gaps in safety chains immediately
- **Traceability**: Complete hazard → goal → requirement → test chains
- **Discrepancy Analysis**: Compare predicted vs observed risks from field data
- **Weak Link Detection**: Identify safety-critical architectural hubs
- **Fault Tree Synthesis**: Auto-generate fault trees from knowledge graph patterns

## 📋 Project Status

**Current Phase**: Planning / Initial Setup
**Version**: 0.1.0 (Development)

### Implementation Roadmap

- ✅ **Phase 0**: Project setup and infrastructure
- 🚧 **Phase 1 (M1)**: Core Knowledge Graph & ETL
- ⏳ **Phase 2 (M2)**: Frontend & Visualization
- ⏳ **Phase 3 (M3)**: Runtime Defects Integration
- ⏳ **Phase 4 (M4)**: Advanced Graph Analytics
- 📅 **Phase 5**: STPA Integration

## 🛠️ Technology Stack

### Backend
- **Graph Database**: Neo4j 5.15+ (Community Edition)
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11+
- **Validation**: Pydantic v2
- **Analytics**: python-igraph
- **Dependency Management**: Poetry 1.8+

### Frontend
- **Framework**: React 18 + TypeScript 5
- **Build Tool**: Vite 5
- **UI Components**: Material-UI (MUI)
- **Graph Visualization**: Cytoscape.js
- **State Management**: TanStack Query (server state) + Zustand (local state)
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Testing**: pytest (backend), Vitest (frontend)
- **Code Quality**: Black, Ruff, mypy (backend), ESLint, Prettier (frontend)

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (recommended for easiest setup)
- **OR** Local installation:
  - Python 3.11+
  - Node.js 20+
  - Neo4j 5.15+ (Community or Enterprise)
  - Poetry 1.8+

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ProjectA
   ```

2. **Create environment files**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize Neo4j schema** (first time only)
   ```bash
   docker-compose exec backend python scripts/init_schema.py
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474 (user: neo4j, password: safetygraph123)

### Option 2: Local Development Setup

#### Backend Setup

1. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Navigate to backend directory**
   ```bash
   cd backend
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Create and configure .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j connection details
   ```

5. **Start Neo4j** (if running locally)
   ```bash
   # Follow Neo4j installation instructions for your OS
   # Or use Docker:
   docker run -d \
     --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/safetygraph123 \
     -e NEO4J_PLUGINS='["apoc"]' \
     neo4j:5.15-community
   ```

6. **Run the backend**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

7. **Initialize schema** (first time only)
   ```bash
   poetry run python scripts/init_schema.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create and configure .env file**
   ```bash
   cp .env.example .env
   # Edit .env if backend is not at http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## 📚 Documentation

- **[claude.md](./claude.md)**: Complete project context for AI assistants (architecture, tech stack, guidelines)
- **[TODO.md](./TODO.md)**: Comprehensive implementation task list for all phases
- **[PRDs](./docs/prds/)**: Product Requirements Documents for each phase
  - [Phase 1: Core KG & ETL](./docs/prds/prd-phase1.md)
  - [Phase 2: Frontend & Visualization](./docs/prds/prd-phase2.md)
  - [Phase 3: Runtime Defects Integration](./docs/prds/prd-phase3.md)
  - [Phase 4: Advanced Analytics](./docs/prds/prd-phase4.md)

## 🗂️ Project Structure

```
ProjectA/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Neo4j driver and queries
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # pytest tests
│   ├── scripts/            # Utility scripts
│   ├── pyproject.toml      # Poetry dependencies
│   └── Dockerfile
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API client
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utilities
│   ├── tests/              # Vitest tests
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── seed/               # Example seed data
│   └── schema/             # Neo4j schema scripts
├── docs/
│   └── prds/               # Product requirements
├── docker-compose.yml
├── README.md               # This file
├── claude.md               # Project context
└── TODO.md                 # Implementation tasks
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_models.py

# Run with verbose output
poetry run pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm run test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test -- --watch
```

### Linting and Formatting

**Backend:**
```bash
cd backend

# Format code
poetry run black app tests

# Lint code
poetry run ruff check app tests

# Type check
poetry run mypy app
```

**Frontend:**
```bash
cd frontend

# Lint
npm run lint

# Format
npm run format

# Type check
npm run type-check
```

## 🔧 Development Workflow

### Adding a New Feature

1. Check `TODO.md` for the relevant milestone tasks
2. Review the corresponding PRD in `docs/prds/`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Implement with tests (aim for >80% coverage)
5. Run linters and tests
6. Commit and push
7. Create pull request

### Backend Development

1. Add Pydantic models in `app/models/`
2. Create Cypher queries in `app/db/queries.py`
3. Implement service logic in `app/services/`
4. Create API endpoints in `app/api/endpoints/`
5. Write tests in `tests/`
6. Update API docs (auto-generated by FastAPI)

### Frontend Development

1. Add TypeScript types in `src/types/`
2. Create API hooks in `src/hooks/`
3. Build components in `src/components/`
4. Create pages in `src/pages/`
5. Write tests in `tests/`
6. Update documentation

## 📊 Example Usage

### Import HARA Data (API)

```bash
curl -X POST http://localhost:8000/import/hara \
  -H "Content-Type: application/json" \
  -d @data/seed/hara_example.json
```

### Query Hazard Coverage

```bash
curl http://localhost:8000/analytics/hazard-coverage?asil=D
```

### Analyze Component Impact

```bash
curl http://localhost:8000/analytics/impact/component/C-INV-001
```

### Using the Frontend

1. Navigate to http://localhost:3000
2. View the dashboard for overview statistics
3. Go to "Hazard Coverage" to see coverage status
4. Use "Impact Explorer" to analyze component changes
5. Explore "Graph Visualization" for interactive exploration

## 🐛 Troubleshooting

### Neo4j Connection Issues

- Ensure Neo4j is running: `docker-compose ps neo4j`
- Check Neo4j logs: `docker-compose logs neo4j`
- Verify connection in Neo4j Browser: http://localhost:7474
- Check credentials in `.env` file

### Backend Won't Start

- Ensure Python 3.11+ is installed: `python --version`
- Verify Poetry installation: `poetry --version`
- Check for dependency conflicts: `poetry install`
- View backend logs: `docker-compose logs backend`

### Frontend Build Errors

- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 20+)
- Verify API connection in browser console
- Check frontend logs: `docker-compose logs frontend`

### Port Conflicts

If ports 3000, 7474, 7687, or 8000 are already in use:
1. Stop conflicting services
2. OR modify ports in `docker-compose.yml`
3. Update corresponding `.env` files

## 🤝 Contributing

This is currently a planning and development project. Contributions will be welcome once core functionality is implemented.

### Code Style

- **Backend**: Follow PEP 8, use Black formatter, pass Ruff linting
- **Frontend**: Follow Airbnb style guide, use Prettier, pass ESLint
- **Commits**: Use conventional commits format
- **Tests**: Required for all new features (>80% coverage goal)

## 📄 License

[License TBD]

## 🙏 Acknowledgments

This project is inspired by:
- SafetyLens (VIS 2020) - Visualization of safety artifact linkages
- Academic work on knowledge graphs for safety analysis
- ISO 26262:2018 standard for functional safety
- STPA (Systems-Theoretic Process Analysis) methodology

## 📞 Contact

[Contact information TBD]

---

**Project Status**: Active Development (Phase 0 Complete)
**Last Updated**: 2025-11-18
**Next Milestone**: M1 - Core KG & ETL
