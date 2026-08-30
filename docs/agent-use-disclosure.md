# Agent & Tool Use Disclosure — HandWrite Verify

This document explicitly details all AI assistants, agent frameworks, subagents, and automated tooling used during the development of HandWrite Verify.

---

## Tool Disclosure Matrix

| Tool / Agent Name | Purpose & Function | Where Used in Repository | Code / Doc / Test / Asset Generation | Disclosure Mode | Trajectory Retained |
|---|---|---|---|---|---|
| **Antigravity AI (Gemini 3.6 Flash / Pro)** | Primary pair-programming agent & project coordinator | Entire codebase, scripts, specs, and documentation | Generated code (`app/`, `scripts/`, `tests/`), schemas, and docs | Full repository disclosure | Yes (`transcript.jsonl` & `.agent/workflows/`) |
| **Research Subagent** | Codebase inspection & background environment analysis | Local repository workspace discovery | None (read-only research) | Full repository disclosure | Yes |
| **Pillow (PIL)** | Synthetic form image rendering & evidence crop generation | `scripts/generate_synthetic_corpus.py` & `app/backend/agents/quality_agent.py` | Generated synthetic document images (`data/synthetic/`) | Script output disclosure | Yes (`data/manifests/manifest.json`) |
| **FastAPI / Pydantic v2** | Backend REST API server & typed data contract validation | `app/backend/main.py` & `app/shared/schemas.py` | Generated API routes & validation logic | Source code | Yes (`tests/test_api.py`) |
| **Vite / React 18** | Reviewer SPA interface & dual-pane workspace | `app/frontend/src/App.jsx` | Generated frontend component logic | Source code | Yes (`dist/assets/`) |
| **Pytest Test Runner** | Automated schema validation & pipeline regression testing | `scripts/run_schema_tests.py` & `tests/` | None (executes unit test suites) | Terminal output | Yes (test run outputs) |

---

## Declaration of Human Oversight
All agent-generated code, schemas, verification rules, evaluation harnesses, and documentation were explicitly requested, reviewed, tested, and approved by the human participant, **Victor Sabo**.
