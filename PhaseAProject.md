Project A – “Safety Graph Twin”: Knowledge Graph for ISO 26262 + Root Cause

1. Concept & why it’s interesting

Goal:
Build a Safety Graph Twin of a system: a knowledge graph that links:
	•	SysML-ish architecture (blocks, functions, signals)
	•	HARA / SOTIF artifacts (hazards, situations, scenarios, ASIL)
	•	Safety analyses (FMEA, FTA, FMEDA)
	•	Requirements & tests
	•	Field defects / events (from your defect KG idea)

So you can ask:
	•	“Which ASIL-D safety goals are supported only by a single mitigation with weak test coverage?”
	•	“A defect just appeared on inverter gate driver X – which hazards, safety goals and tests are impacted?”
	•	“Where are there gaps between FMEA → FTA → test evidence?”

There’s recent work that goes in this direction, but usually in siloed tools:
	•	SafetyLens (VIS 2020) visualizes linkages between hazards, malfunctions, requirements, tests for ISO 26262, but doesn’t push hard on graph analytics.  ￼
	•	Knowledge-graph approaches that unify multiple safety methods (FMEA, HAZOP, FTA, bow-tie) into one KG for proactive safety analysis.  ￼
	•	Model-based safety analysis using SysML + automatic FTA generation from system models.  ￼
	•	Recent work on fault tree synthesis from knowledge graphs shows you can generate FT from structural/functional KG.  ￼

You’d effectively build an open, developer-friendly version of this, designed to tie into your operations defect KG.

⸻

2. Scope: v1 vs v2

v1: “Design & Analysis Graph”
	•	Import static lifecycle artifacts:
	•	Simplified architecture model (YAML/JSON; later SysML XMI)
	•	HARA entries (Hazard, Operating Scenario, ASIL, Safety Goal)
	•	FMEA entries (Item, Function, Failure Mode, Cause, Effect, Detection, RPN)
	•	FTA structures (basic events, gates, top events)
	•	Requirements & test cases (at least IDs and trace links)
	•	Build a Neo4j (or similar) KG that supports:
	•	Change impact queries
	•	Coverage/gap analysis (hazard→goal→req→test)
	•	Simple centrality metrics to find “safety critical hubs”

v2: “Closed Loop Safety Graph”
	•	Ingest runtime defects / events from your field / line:
	•	Defect instances, CV anomalies, warranty claims
	•	Link them back into the Safety Graph:
	•	DefectInstance → (Component, FailureMode, Hazard, SafetyGoal)
	•	Perform continuous discrepancy analysis:
	•	Hazards with many real defects but low risk rating
	•	Requirements with tests “passing” but correlated with field incidents

⸻

3. Core graph schema (first pass)

You’ll likely refine this, but a good starting point:

Node types
	•	Item – high-level system or subsystem (e.g., “HV Battery System”)
	•	Function – logical/functional block (e.g., “Torque Control”, “Brake Blending”)
	•	Component – concrete HW/SW element (ECU, sensor, inverter, SW module)
	•	Signal – logical or physical signal (e.g., TorqueCmd, WheelSpeed_FL)
	•	Hazard – hazardous event description
	•	Scenario – operating scenario / ODD slice (especially for SOTIF/ADS)  ￼
	•	SafetyGoal – from HARA
	•	FunctionalSafetyRequirement (FSR)
	•	TechnicalSafetyRequirement (TSR)
	•	TestCase – verification/validation artifact
	•	FMEAEntry – or split into FailureMode, Cause, Effect
	•	FTEvent – for Fault Tree nodes (basic, intermediate, top)
	•	DefectInstance / FieldEvent – runtime issues
	•	StandardClause – optional, map to ISO 26262 / ISO 21434 clauses  ￼

Relationships (examples)
	•	Architecture
	•	(Item)-[:HAS_FUNCTION]->(Function)
	•	(Function)-[:REALIZED_BY]->(Component)
	•	(Function)-[:USES_SIGNAL]->(Signal)
	•	(Component)-[:CONNECTED_TO]->(Component)
	•	Safety concept / HARA
	•	(Hazard)-[:IN_SCENARIO]->(Scenario)
	•	(Hazard)-[:MITIGATED_BY]->(SafetyGoal)
	•	(SafetyGoal)-[:REFINED_INTO]->(FunctionalSafetyRequirement)
	•	(FunctionalSafetyRequirement)-[:ALLOCATED_TO]->(Item|Function|Component)
	•	Detailed analysis
	•	(FMEAEntry)-[:FOR_FUNCTION]->(Function)
	•	(FMEAEntry)-[:HAS_FAILURE_MODE]->(FailureMode)
	•	(FailureMode)-[:CAN_LEAD_TO]->(Hazard)
	•	(FTEvent)-[:CAUSES]->(FTEvent)
	•	(FTEvent)-[:ASSOCIATED_WITH]->(FailureMode|Component)
	•	V&V
	•	(FunctionalSafetyRequirement|TechnicalSafetyRequirement)-[:VERIFIED_BY]->(TestCase)
	•	(TestCase)-[:COVERS_SIGNAL]->(Signal)
	•	Runtime
	•	(DefectInstance)-[:OBSERVED_AT]->(Component)
	•	(DefectInstance)-[:INSTANCE_OF]->(FailureMode)
	•	(DefectInstance)-[:RELATED_TO]->(Hazard)

This schema is compatible with the minimal KG → FTA synthesis format people are exploring now.  ￼

⸻

4. Architecture & tech stack

Backend
	•	Graph DB: Neo4j or Memgraph (good ecosystem; Cypher is pleasant).
	•	Service layer: Python + FastAPI:
	•	ETL endpoints (upload CSV/YAML)
	•	Query endpoints (predefined analytics)
	•	Optional “Cypher sandbox” for power users

Front-end
	•	React + TypeScript:
	•	“Safety Overview” dashboards
	•	Graph visualizations (e.g., using Cytoscape.js)
	•	Panels for hazards, requirements, tests

Data ingestion
	•	Start with CSV/YAML ingestion:
	•	hara.csv, fmea.csv, fta.json, requirements.csv, tests.csv
	•	Later: import SysML XMI (e.g., from Cameo/Capella)  ￼

⸻

5. Key graph analyses (what makes it useful)

Examples of core analytics:
	1.	Coverage of hazards / goals
	•	Cypher query to find Hazard nodes not connected to any TestCase through the chain Hazard → SafetyGoal → FSR/TSR → TestCase.
	•	Graph metric: proportion of hazards with at least one “test chain”.
	2.	Weak links / single points of safety failure
	•	Find Component or Function nodes with high betweenness centrality on paths from SafetyGoal to TestCase.
	•	These are safety-critical hubs; changes here should trigger big impact analysis.
	3.	Change impact
	•	Given a modified Component, traverse:
Component → (FailureModes, FMEAEntries, FTEvents, Requirements, TestCases, Hazards)
	•	Provide this as an API to be called from your CI/CD (e.g., if certain files/components changed, list impacted safety items).
	4.	Design vs runtime discrepancy
	•	Link runtime DefectInstance to FailureMode / Component.
	•	Compare observed defect rates per hazard vs. risk estimates in HARA (ASIL vs real-world frequency/severity).
	5.	Automatic FTA support (v2+)
	•	Use KG patterns (AND/OR relationships between causes/effects) to synthesize or update fault trees automatically, inspired by the KG→FTA work.  ￼

⸻

6. Milestones for an AI coder

M1 – Core KG & ETL
	•	Define Neo4j schema and constraints.
	•	Implement FastAPI service with:
	•	POST /import/hara
	•	POST /import/fmea
	•	POST /import/requirements
	•	POST /import/tests
	•	Implement Cypher for:
	•	“hazard coverage” query
	•	“impact from component X” query

M2 – Frontend & Visualization
	•	React app:
	•	List of hazards with coverage status (no test / partial / full).
	•	Drilldown view: hazard → goals → requirements → tests chain.
	•	Graph visualization of neighborhood around:
	•	A Component
	•	A Hazard

M3 – Runtime Defects Integration
	•	Add DefectInstance import.
	•	Implement discrepancy analysis:
	•	For each Hazard, show predicted risk vs. observed defect count.

M4 – Advanced Graph Analytics
	•	Implement:
	•	Centrality metrics (via APOC or Python + NetworkX on subgraphs).
	•	Preliminary algorithm to propose FT structure from local KG patterns.

⸻

7. “Master prompt” you can give an AI coder (Safety Graph Twin)

You can trim/modify this, but here’s a ready-to-paste spec:

You are building a “Safety Graph Twin” for an automotive/robotics system, aligned with ISO 26262.

Goal: Represent architecture, hazards, safety goals, FMEA, fault trees, requirements, tests, and runtime defects in a Neo4j knowledge graph, and expose useful safety analytics via an API and a small web UI.

Tech stack:
	•	Backend: Python 3.11, FastAPI, Neo4j (official Python driver), Poetry for deps.
	•	Frontend: React + TypeScript + Vite, using a simple graph visualization lib (e.g., Cytoscape.js).

Phase 1 – Data model & ETL
	1.	Define a Neo4j schema with these node labels and key properties:
	•	Item(id, name)
	•	Function(id, name)
	•	Component(id, name, type)
	•	Signal(id, name)
	•	Hazard(id, description, asil)
	•	Scenario(id, name)
	•	SafetyGoal(id, description, asil)
	•	FunctionalSafetyRequirement(id, text)
	•	TechnicalSafetyRequirement(id, text)
	•	TestCase(id, name, status)
	•	FMEAEntry(id, failure_mode, effect, cause, detection, rpn)
	•	FTEvent(id, type, description)
	•	DefectInstance(id, timestamp, severity)
	2.	Define relationships:
	•	(Item)-[:HAS_FUNCTION]->(Function)
	•	(Function)-[:REALIZED_BY]->(Component)
	•	(Function)-[:USES_SIGNAL]->(Signal)
	•	(Hazard)-[:IN_SCENARIO]->(Scenario)
	•	(Hazard)-[:MITIGATED_BY]->(SafetyGoal)
	•	(SafetyGoal)-[:REFINED_INTO]->(FunctionalSafetyRequirement)
	•	(FunctionalSafetyRequirement)-[:ALLOCATED_TO]->(Item|Function|Component)
	•	(FunctionalSafetyRequirement|TechnicalSafetyRequirement)-[:VERIFIED_BY]->(TestCase)
	•	(FMEAEntry)-[:FOR_FUNCTION]->(Function)
	•	(FMEAEntry)-[:HAS_FAILURE_MODE]->(:FailureMode {name}) (create if not exists)
	•	(:FailureMode)-[:CAN_LEAD_TO]->(Hazard)
	•	(FTEvent)-[:CAUSES]->(FTEvent)
	•	(FTEvent)-[:ASSOCIATED_WITH]->(FailureMode|Component)
	•	(DefectInstance)-[:OBSERVED_AT]->(Component)
	•	(DefectInstance)-[:INSTANCE_OF]->(FailureMode)
	3.	Implement FastAPI endpoints to import CSV files:
	•	POST /import/hara – payload with Hazards, Scenarios, SafetyGoals and their links.
	•	POST /import/fmea – payload with FMEA entries, Functions, FailureModes, and links to Hazards.
	•	POST /import/requirements – payload with FSR/TSR and allocation links.
	•	POST /import/tests – payload with TestCases and their links to requirements.
	•	POST /import/defects – payload with DefectInstances linked to Components and FailureModes.
	4.	Implement Cypher queries and wrap them in endpoints:
	•	GET /analytics/hazard-coverage – for each Hazard, return whether there is at least one TestCase reachable via SafetyGoal→FSR/TSR→TestCase; include IDs of the chain.
	•	GET /analytics/impact/component/{component_id} – return all Hazards, Requirements, TestCases, FMEAEntries and FTEvents reachable from the Component within 4 hops.

Phase 2 – Frontend
	1.	Create a React UI with pages:
	•	“Hazard Coverage”: table of Hazards with coverage status and a button to show the chain.
	•	“Impact Explorer”: enter a Component ID, call the impact endpoint, and show a graph visualization of the local neighborhood.
	2.	Keep styling simple; prioritize clear visual representation of relationships.

Deliverables
	•	A docker-compose that spins up Neo4j + backend + frontend.
	•	Seed scripts with example CSVs so I can demo end-to-end.
	•	Clear README with how to run and example queries.

Implement Phase 1 fully before starting Phase 2. Focus on correctness, clear structure, and testable units.

⸻
