# Product Requirements Document: Phase 2 - Frontend & Visualization

**Project:** Safety Graph Twin
**Phase:** M2 - Frontend & Visualization
**Version:** 1.0
**Date:** 2025-11-18
**Status:** Planning
**Dependencies:** Phase 1 (Core KG & ETL) must be complete

---

## 1. Executive Summary

### 1.1 Overview

Phase 2 delivers an interactive web-based user interface for the Safety Graph Twin, enabling safety engineers and systems engineers to visualize, explore, and analyze safety artifacts through intuitive dashboards and graph visualizations. This phase transforms the backend API (Phase 1) into a production-ready tool accessible to non-technical stakeholders.

### 1.2 Business Objectives

- **Democratize Safety Insights:** Enable non-technical users (managers, auditors) to access safety analytics
- **Improve Decision Speed:** Reduce time to answer "what's the impact?" from hours to seconds
- **Enhance Visibility:** Provide real-time dashboards showing coverage gaps and safety status
- **Enable Exploration:** Interactive graph visualization for discovering unexpected relationships

### 1.3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page Load Time | <2 seconds (P95) | Performance monitoring |
| Query Response Time | <1 second for analytics | API latency tracking |
| Graph Render Performance | 100+ nodes at 60fps | Performance profiling |
| User Task Completion | >90% success rate | Usability testing |
| Mobile Responsiveness | Functional on tablet/desktop | Cross-device testing |

---

## 2. Problem Statement

### 2.1 Current Pain Points

**For Safety Engineers:**
- Backend API requires technical knowledge (cURL, Postman)
- No visual way to explore relationships in safety graph
- Cannot share results with non-technical stakeholders easily
- Difficult to spot patterns across multiple artifacts

**For Managers/Auditors:**
- Cannot access safety status without requesting reports from engineers
- No real-time visibility into coverage or gaps
- Cannot drill down into specific hazards or components themselves

**For Systems Engineers:**
- Impact analysis results are JSON - hard to interpret quickly
- Cannot visualize "blast radius" of component changes
- No way to explore graph interactively

### 2.2 Target Users

**Primary:**
- Functional Safety Engineers (daily users, exploratory analysis)
- Systems Engineers (impact analysis before design changes)

**Secondary:**
- Project Managers (dashboards for project health)
- Auditors (compliance evidence gathering)
- Test Engineers (traceability verification)

---

## 3. Requirements

### 3.1 Functional Requirements

#### FR1: Application Shell & Navigation

**FR1.1 Layout**
- MUST provide responsive layout (desktop: 1920x1080, laptop: 1366x768, tablet: 1024x768)
- MUST include persistent navigation sidebar/header
- MUST display current user context (if auth implemented)
- SHOULD collapse navigation on mobile/tablet

**FR1.2 Routing**
- MUST support client-side routing (no full page reloads)
- MUST provide routes for:
  - `/` - Dashboard (home)
  - `/hazards` - Hazard Coverage view
  - `/impact` - Impact Explorer
  - `/graph` - Graph Visualization
  - `/import` - Data Import UI (optional in v1)
- MUST support deep linking (shareable URLs)
- SHOULD support browser back/forward navigation

**FR1.3 Error Handling**
- MUST display user-friendly error messages for API failures
- MUST provide retry mechanism for failed requests
- MUST show loading states for all async operations
- SHOULD show toast/snackbar notifications for success/error events

#### FR2: Dashboard / Home Page

**FR2.1 Overview Statistics**
- MUST display key metrics:
  - Total hazards (with breakdown by ASIL)
  - Coverage percentage (overall)
  - Number of gaps (requirements without tests, hazards without coverage)
  - Total components, requirements, tests
- MUST update statistics in real-time (or on page load)
- SHOULD display trend indicators (if historical data available)

**FR2.2 Visual Summaries**
- MUST display coverage pie/donut chart (full, partial, none)
- MUST display ASIL distribution bar chart
- SHOULD display recent imports or activity log
- SHOULD display "top 5 at-risk hazards" (ASIL-D with no coverage)

**FR2.3 Quick Actions**
- SHOULD provide quick links to common tasks:
  - "View all uncovered hazards"
  - "Analyze impact of component X"
  - "Import new data"

#### FR3: Hazard Coverage View

**FR3.1 Data Table**
- MUST display table with columns:
  - Hazard ID
  - Description (truncated, with tooltip for full text)
  - ASIL (color-coded badge)
  - Coverage Status (color-coded: green=full, yellow=partial, red=none)
  - Actions (View Chain button)
- MUST support sorting by any column
- MUST support filtering by:
  - ASIL level (multi-select dropdown)
  - Coverage status (multi-select dropdown)
  - Text search in description
- MUST support pagination (default 50 rows per page)
- SHOULD support export to CSV

**FR3.2 Coverage Status Indicators**
- MUST use consistent color coding:
  - Green: Full coverage (all paths reach passed tests)
  - Yellow: Partial coverage (some paths missing tests or tests failed)
  - Red: No coverage (no path to any test)
- MUST show icon or badge for quick visual scanning

**FR3.3 Traceability Chain Drilldown**
- MUST provide "View Chain" action for each hazard
- MUST display modal/sidebar with full traceability:
  - Hazard → Safety Goals → FSR → TSR → Test Cases
  - Show all paths (if multiple safety goals)
  - Highlight missing links in red
  - Show test status (passed/failed/not_run/blocked) with color coding
- MUST support click-through to view details of any artifact
- SHOULD support export of chain as image or PDF

#### FR4: Impact Explorer

**FR4.1 Component Selection**
- MUST provide component selector:
  - Dropdown with autocomplete/search
  - OR searchable list with filtering
- MUST display component details when selected:
  - ID, Name, Type, Version
- SHOULD show component hierarchy (if available)

**FR4.2 Impact Analysis Results**
- MUST display list of impacted artifacts grouped by type:
  - Hazards (with ASIL and description)
  - Safety Goals
  - Requirements (FSR/TSR)
  - Test Cases (with status)
  - FMEA Entries (with RPN)
  - FT Events (if available)
- MUST show path length (number of hops) for each artifact
- MUST support sorting by: path length, ASIL, RPN
- SHOULD highlight ASIL-C/D artifacts for criticality
- SHOULD show summary statistics:
  - Total impacted artifacts
  - Count by type
  - Critical artifacts (ASIL-C/D)

**FR4.3 Impact Visualization**
- MUST provide graph visualization of impact:
  - Component at center
  - Related nodes positioned around it
  - Edges showing relationships
- MUST support interactivity:
  - Click node to see details
  - Hover for tooltip
  - Zoom and pan
- MUST use distinct visual encoding:
  - Node color by type (Hazard, Requirement, Test, etc.)
  - Node size by criticality (larger for ASIL-D)
  - Edge style by relationship type (solid, dashed, dotted)
- SHOULD support layout algorithms (force-directed, hierarchical, radial)
- SHOULD support filtering visible node types

#### FR5: Graph Visualization Page

**FR5.1 Full Graph Visualization**
- MUST support rendering graphs up to 500 nodes (performance target)
- MUST provide controls:
  - Zoom in/out (buttons + mouse wheel)
  - Pan (click-drag)
  - Reset view (fit to screen)
  - Search/highlight node by ID or name
- MUST support layout algorithms:
  - Force-directed (default)
  - Hierarchical (top-down tree)
  - Circular/radial
- SHOULD support export as image (PNG/SVG)

**FR5.2 Node and Edge Styling**
- MUST use distinct visual encoding:
  - **Node shapes:** Circle (default), Rectangle (components), Diamond (hazards), Hexagon (tests)
  - **Node colors:** By type (configurable palette)
  - **Node size:** By importance (ASIL level, centrality if available)
  - **Edge colors:** By relationship type
  - **Edge thickness:** By strength/frequency (if applicable)
- MUST show node labels (truncated if needed)
- MUST show relationship labels on hover or always visible (configurable)

**FR5.3 Interactivity**
- MUST support node selection (click to select, multi-select with Ctrl/Cmd)
- MUST display node details panel when selected:
  - All properties
  - Incoming and outgoing relationships
  - Quick actions (view neighbors, hide node, etc.)
- MUST support "expand neighborhood" action (load related nodes on demand)
- SHOULD support "hide node" action (temporary filter)
- SHOULD support "pin node" action (fix position during layout)

**FR5.4 Filters and Search**
- MUST provide filters:
  - Node type (multi-select checkboxes)
  - ASIL level (multi-select)
  - Relationship type (multi-select)
- MUST provide search box:
  - Search by ID, name, description (autocomplete)
  - Highlight matching nodes
- SHOULD support "shortest path" finder (select two nodes, show path)

#### FR6: Data Import UI (Optional)

**FR6.1 File Upload**
- MAY provide UI for importing data (alternative to API/cURL)
- If implemented, MUST support:
  - File selection (CSV or JSON)
  - Preview of data before import
  - Validation errors shown inline
  - Import progress indicator
  - Success/error summary after import

**FR6.2 Import Templates**
- SHOULD provide downloadable CSV templates
- SHOULD include example data in templates
- SHOULD validate CSV structure before upload

### 3.2 Non-Functional Requirements

#### NFR1: Performance

- Page load (initial): <2 seconds (P95)
- Page transitions: <500ms (P95)
- API query execution: <1 second (P95, backend SLA)
- Graph rendering: 60fps for graphs up to 100 nodes
- Graph rendering: 30fps for graphs up to 500 nodes
- Bundle size: <1MB (gzipped JS)

#### NFR2: Usability

- MUST be operable with keyboard only (accessibility)
- MUST meet WCAG 2.1 AA accessibility standards
- MUST provide consistent color scheme and typography
- MUST have intuitive navigation (usability testing >90% task success)
- SHOULD support dark mode (optional in v1)

#### NFR3: Compatibility

- MUST support modern browsers:
  - Chrome/Edge 120+
  - Firefox 120+
  - Safari 17+
- MUST be responsive (desktop, laptop, tablet)
- Mobile support is OPTIONAL in v1 (read-only acceptable)

#### NFR4: Maintainability

- MUST use TypeScript with strict mode
- MUST have component documentation (props, usage)
- MUST use ESLint and Prettier for code quality
- SHOULD achieve >70% test coverage on components
- SHOULD use Storybook for component documentation (optional)

#### NFR5: Security

- MUST sanitize all user inputs (XSS prevention)
- MUST use HTTPS in production
- MUST implement CORS correctly with backend
- SHOULD implement Content Security Policy headers

---

## 4. Technical Architecture

### 4.1 Technology Stack

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Framework | React | 18.2+ | Mature, large ecosystem, excellent TypeScript support |
| Language | TypeScript | 5.0+ | Type safety, better DX, catches errors at compile time |
| Build Tool | Vite | 5.0+ | Fast HMR, optimized bundling, modern DX |
| Routing | React Router | 6.20+ | De facto standard, supports nested routes |
| State Management | TanStack Query (React Query) | 5.0+ | Server state caching, automatic refetching, excellent DX |
| Local State | Zustand OR React Context | 4.4+ | Lightweight, simple API, good TypeScript support |
| Graph Visualization | ReactFlow (XyFlow) | 11.10+ | Modern, React-native, interactive, extensible |
| Alternative Graph Lib | Cytoscape.js | 3.28+ | Powerful layouts, mature, battle-tested |
| UI Components | shadcn/ui OR MUI | Latest | Accessible, customizable, TypeScript-native |
| Charting | Recharts | 2.10+ | React-native, composable, good for simple charts |
| HTTP Client | Axios | 1.6+ | Interceptors, better error handling than fetch |
| Testing | Vitest + React Testing Library | Latest | Fast, Vite-native, excellent React support |
| Linting | ESLint | 8.0+ | Industry standard |
| Formatting | Prettier | 3.0+ | Consistent code style |

### 4.2 Architecture Pattern

**Frontend Architecture:**
- **Presentation Layer:** React components (pages, shared components)
- **State Layer:** TanStack Query (server state) + Zustand/Context (UI state)
- **Service Layer:** API client (Axios wrapper)
- **Type Layer:** TypeScript interfaces/types matching backend schemas

**Folder Structure:**
```
frontend/
├── src/
│   ├── components/         # Shared/reusable components
│   │   ├── ui/            # Basic UI components (Button, Card, etc.)
│   │   ├── layout/        # Layout components (Header, Sidebar, etc.)
│   │   ├── graph/         # Graph visualization components
│   │   ├── charts/        # Chart components
│   │   └── shared/        # Domain-specific shared components
│   ├── pages/             # Page components (routes)
│   │   ├── Dashboard.tsx
│   │   ├── HazardCoverage.tsx
│   │   ├── ImpactExplorer.tsx
│   │   └── GraphVisualization.tsx
│   ├── hooks/             # Custom React hooks
│   │   ├── useHazardCoverage.ts
│   │   ├── useImpactAnalysis.ts
│   │   └── useGraphData.ts
│   ├── services/          # API client and utilities
│   │   ├── api.ts         # Axios instance and interceptors
│   │   ├── queries.ts     # TanStack Query query functions
│   │   └── mutations.ts   # TanStack Query mutation functions
│   ├── types/             # TypeScript type definitions
│   │   ├── nodes.ts       # Node types (Hazard, Component, etc.)
│   │   ├── api.ts         # API request/response types
│   │   └── graph.ts       # Graph visualization types
│   ├── utils/             # Utility functions
│   │   ├── formatters.ts  # Data formatting (dates, numbers, etc.)
│   │   ├── validators.ts  # Client-side validation
│   │   └── constants.ts   # Constants (colors, ASIL values, etc.)
│   ├── styles/            # Global styles, theme
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # Entry point
│   └── router.tsx         # Route configuration
├── public/                # Static assets
├── tests/                 # Test files
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### 4.3 Data Flow

**Query Flow (GET requests):**
```
User Action (click, search, filter)
  ↓
React Component
  ↓
TanStack Query Hook (useQuery)
  ↓
API Service (Axios GET)
  ↓
Backend API
  ↓
Response (JSON)
  ↓
TanStack Query Cache (automatic)
  ↓
React Component Re-render
  ↓
UI Update
```

**Mutation Flow (POST requests for import):**
```
User Action (file upload, form submit)
  ↓
React Component
  ↓
TanStack Query Hook (useMutation)
  ↓
API Service (Axios POST)
  ↓
Backend API
  ↓
Response (success/error)
  ↓
TanStack Query Invalidation (refresh related queries)
  ↓
UI Update (success toast, redirect, etc.)
```

### 4.4 State Management Strategy

**Server State (TanStack Query):**
- Hazard coverage data
- Impact analysis results
- Graph data
- Statistics
- Automatic caching, refetching, and synchronization

**Local UI State (Zustand or React Context):**
- Selected component for impact analysis
- Active filters (ASIL, coverage status, etc.)
- Graph layout preferences
- Theme (light/dark mode)
- Navigation state (sidebar open/closed)

**Component State (useState):**
- Form inputs
- Modal open/closed
- Temporary UI state

---

## 5. User Interface Specification

### 5.1 Dashboard Page

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Header: Safety Graph Twin                      │
│ [User Avatar] [Settings]                        │
├──────┬──────────────────────────────────────────┤
│ Nav  │ Dashboard                                │
│      │                                          │
│ ┌─┐  │ ┌──────────┬──────────┬──────────┐      │
│ │H│  │ │ Hazards  │ Coverage │   Gaps   │      │
│ │o│  │ │   125    │   85%    │    18    │      │
│ │m│  │ └──────────┴──────────┴──────────┘      │
│ │e│  │                                          │
│ └─┘  │ ┌──────────────┬────────────────┐       │
│      │ │  Coverage    │ ASIL Breakdown │       │
│ ┌─┐  │ │  Pie Chart   │   Bar Chart    │       │
│ │H│  │ │              │                │       │
│ │z│  │ └──────────────┴────────────────┘       │
│ │d│  │                                          │
│ │s│  │ ┌──────────────────────────────┐        │
│ └─┘  │ │ Top 5 At-Risk Hazards         │        │
│      │ │ (ASIL-D, No Coverage)         │        │
│ ┌─┐  │ │ - H-001: Unintended accel...  │        │
│ │I│  │ │ - H-015: Battery thermal...   │        │
│ │m│  │ │ ...                           │        │
│ │p│  │ └──────────────────────────────┘        │
│ └─┘  │                                          │
└──────┴──────────────────────────────────────────┘
```

**Components:**
- StatCard (reusable for metrics)
- CoverageChart (pie/donut chart)
- ASILChart (bar chart)
- RiskList (list of at-risk hazards)

### 5.2 Hazard Coverage Page

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Header                                          │
├──────┬──────────────────────────────────────────┤
│ Nav  │ Hazard Coverage                          │
│      │                                          │
│      │ ┌─────────────────────────────────────┐  │
│      │ │ Filters:                            │  │
│      │ │ ASIL: [All ▼] Coverage: [All ▼]     │  │
│      │ │ Search: [____________] [Search]     │  │
│      │ └─────────────────────────────────────┘  │
│      │                                          │
│      │ ┌───────────────────────────────────┐   │
│      │ │ ID   │ Description │ ASIL │ Status│   │
│      │ ├──────┼─────────────┼──────┼───────┤   │
│      │ │H-001 │Unintended...│ [D]  │ ● Full│   │
│      │ │H-002 │Loss of bra..│ [D]  │ ● Part│   │
│      │ │H-003 │Loss of pro..│ [C]  │ ● None│   │
│      │ │...   │...          │ ...  │ ...   │   │
│      │ └───────────────────────────────────┘   │
│      │ [1] [2] [3] ... [10] (Pagination)       │
└──────┴──────────────────────────────────────────┘
```

**Modal (View Chain):**
```
┌─────────────────────────────────────────────────┐
│ Traceability Chain: H-001                      │
│ ┌─────────────────────────────────────────────┐ │
│ │                                             │ │
│ │ [Hazard: H-001]                             │ │
│ │       ↓                                     │ │
│ │ [Safety Goal: SG-001] ────► [SG-002]        │ │
│ │       ↓                           ↓         │ │
│ │ [FSR-001]                   [FSR-002]       │ │
│ │       ↓                           ↓         │ │
│ │ [TC-001] ✓                  [TC-002] ✗      │ │
│ │                                             │ │
│ │ Legend: ✓ Passed  ✗ Failed  ⊗ Missing       │ │
│ └─────────────────────────────────────────────┘ │
│ [Export as PDF] [Close]                        │
└─────────────────────────────────────────────────┘
```

### 5.3 Impact Explorer Page

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Header                                          │
├──────┬──────────────────────────────────────────┤
│ Nav  │ Impact Explorer                          │
│      │                                          │
│      │ ┌────────────────────────────┐           │
│      │ │ Select Component:          │           │
│      │ │ [Search or select... ▼]    │           │
│      │ └────────────────────────────┘           │
│      │                                          │
│      │ ┌──────────────┬───────────────────────┐ │
│      │ │ Impact List  │ Graph Visualization   │ │
│      │ │              │                       │ │
│      │ │ Hazards (3)  │      [Component]      │ │
│      │ │ - H-001 (D)  │       /   |   \       │ │
│      │ │ - H-005 (C)  │     SG  FMEA  Req     │ │
│      │ │              │      |    |    |      │ │
│      │ │ Safety Goals │     ...  ...  ...     │ │
│      │ │ - SG-001 (D) │                       │ │
│      │ │              │                       │ │
│      │ │ Requirements │                       │ │
│      │ │ - FSR-010    │                       │ │
│      │ │ ...          │                       │ │
│      │ └──────────────┴───────────────────────┘ │
└──────┴──────────────────────────────────────────┘
```

### 5.4 Graph Visualization Page

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Header                                          │
├──────┬──────────────────────────────────────────┤
│ Nav  │ Graph Visualization                      │
│ ┌──┐ │                                          │
│ │Fi│ │ ┌────────────────────────────────────┐   │
│ │lt│ │ │ Controls:                          │   │
│ │er│ │ │ Layout: [Force ▼] [+] [-] [Reset] │   │
│ │s │ │ │ Search: [___________]              │   │
│ │  │ │ └────────────────────────────────────┘   │
│ │□│ │                                          │
│ │H│ │ ┌────────────────────────────────────┐   │
│ │a│ │ │                                    │   │
│ │z│ │ │        ●────●────●                 │   │
│ │d│ │ │       /│    │    │\                │   │
│ │  │ │ │      ● ●   ●    ● ●               │   │
│ │□│ │ │       \ │  / \  / /                │   │
│ │R│ │ │        ●●─●───●●                   │   │
│ │e│ │ │                                    │   │
│ │q│ │ │  (Interactive Graph)               │   │
│ │  │ │ │                                    │   │
│ │□│ │ └────────────────────────────────────┘   │
│ │T│ │                                          │
│ │st│ │ ┌────────────────────────────────────┐  │
│ │  │ │ │ Node Details: Component C-001      │  │
│ │  │ │ │ Name: Inverter Controller          │  │
│ │  │ │ │ Type: Hardware                     │  │
│ │  │ │ │ [View Neighbors] [Hide]            │  │
│ └──┘ │ └────────────────────────────────────┘  │
└──────┴──────────────────────────────────────────┘
```

---

## 6. Component Specification

### 6.1 Shared Components

**StatCard**
```typescript
interface StatCardProps {
  title: string;
  value: number | string;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
}
```
- Displays a single metric with optional trend indicator
- Used on Dashboard for key statistics

**ASILBadge**
```typescript
interface ASILBadgeProps {
  asil: 'A' | 'B' | 'C' | 'D' | 'QM';
  size?: 'sm' | 'md' | 'lg';
}
```
- Color-coded ASIL indicator
- Colors: QM=gray, A=green, B=yellow, C=orange, D=red
- Used throughout app wherever ASIL is displayed

**CoverageStatusBadge**
```typescript
interface CoverageStatusBadgeProps {
  status: 'full' | 'partial' | 'none';
  size?: 'sm' | 'md' | 'lg';
}
```
- Color-coded coverage indicator
- Colors: full=green, partial=yellow, none=red
- Used in Hazard Coverage table

**LoadingSpinner**
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
  message?: string;
}
```
- Animated loading indicator
- Full screen variant for page loads
- Inline variant for component loads

**ErrorAlert**
```typescript
interface ErrorAlertProps {
  error: Error | string;
  onRetry?: () => void;
  dismissible?: boolean;
}
```
- Display error messages
- Optional retry button
- Dismissible with close button

### 6.2 Page-Specific Components

**HazardTable**
```typescript
interface HazardTableProps {
  data: HazardCoverageData[];
  filters: TableFilters;
  onFilterChange: (filters: TableFilters) => void;
  onViewChain: (hazardId: string) => void;
  isLoading: boolean;
}
```
- Data table with sorting, filtering, pagination
- Integrates with TanStack Query for server-side data
- Responsive (stacks on mobile)

**TraceabilityChainModal**
```typescript
interface TraceabilityChainModalProps {
  hazardId: string;
  isOpen: boolean;
  onClose: () => void;
}
```
- Modal displaying full traceability chain
- Fetches data on demand (not preloaded)
- Visual representation with connecting lines

**ImpactGraph**
```typescript
interface ImpactGraphProps {
  componentId: string;
  data: ImpactAnalysisData;
  layout?: 'force' | 'hierarchical' | 'radial';
  onNodeClick?: (node: GraphNode) => void;
}
```
- ReactFlow-based graph visualization
- Interactive (zoom, pan, click)
- Customizable layout

**ComponentSelector**
```typescript
interface ComponentSelectorProps {
  value: string | null;
  onChange: (componentId: string) => void;
  components: Component[];
  isLoading: boolean;
}
```
- Autocomplete dropdown for component selection
- Searchable
- Shows component type and name

### 6.3 Graph Visualization Components

**GraphCanvas**
```typescript
interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  layout: LayoutAlgorithm;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  filters?: NodeFilters;
}
```
- Main graph rendering component
- Wraps ReactFlow or Cytoscape
- Handles layout calculation

**GraphControls**
```typescript
interface GraphControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetView: () => void;
  onLayoutChange: (layout: LayoutAlgorithm) => void;
  currentLayout: LayoutAlgorithm;
}
```
- Control panel for graph interactions
- Zoom, pan reset, layout selection

**NodeDetailsPanel**
```typescript
interface NodeDetailsPanelProps {
  node: GraphNode | null;
  onClose: () => void;
  onExpandNeighbors: () => void;
  onHide: () => void;
}
```
- Side panel showing node details
- Actions: expand neighbors, hide node, etc.

---

## 7. API Integration

### 7.1 API Client Configuration

**Base Configuration:**
```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth token if available)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (handle errors)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized (redirect to login)
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 7.2 TanStack Query Hooks

**useHazardCoverage**
```typescript
import { useQuery } from '@tanstack/react-query';
import api from './api';

export const useHazardCoverage = (filters?: HazardFilters) => {
  return useQuery({
    queryKey: ['hazardCoverage', filters],
    queryFn: async () => {
      const { data } = await api.get('/analytics/hazard-coverage', {
        params: filters,
      });
      return data.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });
};
```

**useImpactAnalysis**
```typescript
export const useImpactAnalysis = (componentId: string | null) => {
  return useQuery({
    queryKey: ['impactAnalysis', componentId],
    queryFn: async () => {
      if (!componentId) return null;
      const { data } = await api.get(`/analytics/impact/component/${componentId}`);
      return data.data;
    },
    enabled: !!componentId, // Only run if componentId is provided
    staleTime: 5 * 60 * 1000,
  });
};
```

**useImportHARA** (Mutation)
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

export const useImportHARA = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: HARAImportRequest) => {
      const response = await api.post('/import/hara', data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries({ queryKey: ['hazardCoverage'] });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
    },
  });
};
```

---

## 8. Testing Strategy

### 8.1 Component Testing

**Unit Tests (Vitest + React Testing Library):**
```typescript
import { render, screen } from '@testing-library/react';
import { ASILBadge } from './ASILBadge';

describe('ASILBadge', () => {
  it('renders ASIL-D with red color', () => {
    render(<ASILBadge asil="D" />);
    const badge = screen.getByText('D');
    expect(badge).toHaveClass('bg-red-500');
  });

  it('renders ASIL-QM with gray color', () => {
    render(<ASILBadge asil="QM" />);
    const badge = screen.getByText('QM');
    expect(badge).toHaveClass('bg-gray-400');
  });
});
```

**Target Coverage:** >70% for components

### 8.2 Integration Testing

**Page-Level Tests:**
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HazardCoverage } from './HazardCoverage';
import { server } from '../mocks/server'; // MSW mock server

describe('HazardCoverage Page', () => {
  it('displays hazards from API', async () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <HazardCoverage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('H-001')).toBeInTheDocument();
      expect(screen.getByText('Unintended acceleration')).toBeInTheDocument();
    });
  });

  it('filters hazards by ASIL', async () => {
    // Test filter functionality
  });
});
```

### 8.3 E2E Testing (Optional)

**Playwright/Cypress:**
```typescript
// e2e/hazard-coverage.spec.ts
test('user can view traceability chain', async ({ page }) => {
  await page.goto('/hazards');

  // Click "View Chain" button for first hazard
  await page.click('[data-testid="view-chain-H-001"]');

  // Modal should appear
  await expect(page.locator('[data-testid="traceability-modal"]')).toBeVisible();

  // Should show safety goal
  await expect(page.locator('text=SG-001')).toBeVisible();
});
```

### 8.4 Visual Regression Testing (Optional)

**Storybook + Chromatic:**
- Create stories for all components
- Automated visual regression testing
- Catch unintended UI changes

---

## 9. Deployment

### 9.1 Docker Configuration

**frontend/Dockerfile:**
```dockerfile
# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf:**
```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  # SPA routing - redirect all to index.html
  location / {
    try_files $uri $uri/ /index.html;
  }

  # API proxy (if needed)
  location /api/ {
    proxy_pass http://backend:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  # Gzip compression
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

### 9.2 Docker Compose Integration

**docker-compose.yml (updated):**
```yaml
version: '3.8'

services:
  neo4j:
    # ... (from Phase 1)

  backend:
    # ... (from Phase 1)

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 9.3 Environment Configuration

**Environment Variables:**
```bash
# .env (development)
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Safety Graph Twin
VITE_ENABLE_DEVTOOLS=true

# .env.production
VITE_API_BASE_URL=https://api.safetygraphtwin.com
VITE_APP_TITLE=Safety Graph Twin
VITE_ENABLE_DEVTOOLS=false
```

---

## 10. Success Criteria

### 10.1 Functional Criteria

- [ ] All pages render without errors
- [ ] Navigation between pages works smoothly
- [ ] Hazard coverage table displays data correctly
- [ ] Filters and search work as expected
- [ ] Traceability chain modal shows complete paths
- [ ] Impact analysis displays all affected artifacts
- [ ] Graph visualization renders and is interactive
- [ ] All API calls handle loading and error states

### 10.2 Performance Criteria

- [ ] Initial page load <2 seconds (P95)
- [ ] Page transitions <500ms (P95)
- [ ] Graph renders 100 nodes at 60fps
- [ ] Bundle size <1MB gzipped
- [ ] Lighthouse score >90 (Performance, Accessibility)

### 10.3 Usability Criteria

- [ ] Usability testing achieves >90% task completion rate
- [ ] WCAG 2.1 AA compliance (keyboard navigation, screen readers)
- [ ] Consistent UI across all pages
- [ ] Clear error messages guide users to resolution
- [ ] Loading states prevent user confusion

### 10.4 Acceptance Criteria

**Demo Scenario:**
1. Open application in browser
2. View dashboard - see summary statistics
3. Navigate to Hazard Coverage - see table of hazards
4. Filter by ASIL-D - see only ASIL-D hazards
5. Click "View Chain" on hazard with no coverage - see empty chain with gap highlighted
6. Navigate to Impact Explorer - select "Inverter Controller" component
7. See list and graph of impacted artifacts
8. Navigate to Graph Visualization - see full graph, interact with nodes

**Acceptance Test:**
- Non-technical user (project manager) can identify ASIL-D hazards without coverage
- Systems engineer can determine impact of component change in <1 minute
- UI is intuitive enough to use without training (based on usability testing)

---

## 11. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Graph performance with large datasets | High | Medium | Implement virtualization, lazy loading, limit initial nodes to 500 |
| ReactFlow learning curve | Medium | Medium | Use Cytoscape.js as fallback, allocate time for ReactFlow R&D |
| API response time degrades UX | High | Low | Implement optimistic UI updates, skeleton loaders, caching |
| Accessibility compliance gaps | Medium | Medium | Use accessible component library (shadcn/MUI), automated a11y testing |
| Browser compatibility issues | Medium | Low | Test on target browsers, use polyfills, transpile for older browsers |
| UI/UX doesn't meet user needs | High | Medium | Conduct user research, iterate on prototypes, usability testing |

---

## 12. Future Enhancements (Out of Scope)

**Deferred to Later:**
- Mobile app (native or PWA)
- Collaborative features (comments, annotations)
- Custom dashboards (user-configurable widgets)
- Real-time updates (WebSocket integration)
- Advanced filtering (saved filters, complex queries)
- Report generation (PDF export of dashboards)
- Dark mode
- Internationalization (i18n)

---

## 13. Appendix

### 13.1 Related Documents

- `prd-phase1.md` - Backend API specification
- `prd-phase3.md` - Runtime Defects PRD
- `prd-phase4.md` - Advanced Analytics PRD
- `claude.md` - Project context
- `TODO.md` - Implementation tasks

### 13.2 References

- React Documentation: https://react.dev/
- ReactFlow Documentation: https://reactflow.dev/
- TanStack Query Documentation: https://tanstack.com/query/
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/

---

**Document Status:** Draft
**Last Updated:** 2025-11-18
**Dependencies:** Phase 1 must be complete before starting Phase 2
**Owner:** Frontend Team
