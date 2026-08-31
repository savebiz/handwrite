# Agent & Tool Use Disclosure — HandWrite Verify

This document explicitly details all AI assistants, agent frameworks, subagents, and automated tooling used during the development of HandWrite Verify.

---

## Trajectory Index & Evidence Catalog
Master Trajectory Index: [docs/trajectory-index.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/trajectory-index.md)

| Trajectory ID | Role / Agent Name | Primary Task | Trajectory JSON Log Path | Evidence File |
|---|---|---|---|---|
| `traj-01-planning-orchestration` | `Project Coordination Lead` | Workspace discovery & roadmap planning | [logs/trajectories/traj-01-planning-orchestration.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-01-planning-orchestration.json) | `walkthrough.md` |
| `traj-02-baseline-extraction` | `Baseline Extraction Runner` | Single-pass baseline extraction | [logs/trajectories/traj-02-baseline-extraction.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-02-baseline-extraction.json) | `outputs/baseline-results.json` |
| `traj-03-intake-quality` | `Document Quality Specialist` | 9 PIL pre-screening quality checks | [logs/trajectories/traj-03-intake-quality.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-03-intake-quality.json) | `scripts/run_intake_quality_tests.py` |
| `traj-04-schema-extraction` | `Handwriting Extraction Specialist` | Schema-guided extraction & crop PNG creation | [logs/trajectories/traj-04-schema-extraction.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-04-schema-extraction.json) | `scripts/run_extraction_tests.py` |
| `traj-05-deterministic-verification` | `Verification & Triage Specialist` | 10 deterministic validation rules | [logs/trajectories/traj-05-deterministic-verification.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-05-deterministic-verification.json) | `scripts/run_verification_tests.py` |
| `traj-06-triage-decision` | `Triage & Decision Agent` | Decision table policy matrix resolution | [logs/trajectories/traj-06-triage-decision.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-06-triage-decision.json) | `scripts/run_triage_tests.py` |
| `traj-07-reviewer-workflow` | `Reviewer Experience Specialist` | Human review UI & export guardrails | [logs/trajectories/traj-07-reviewer-workflow.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-07-reviewer-workflow.json) | `scripts/run_reviewer_tests.py` |
| `traj-08-comparative-evaluation` | `Evaluation Benchmark Specialist` | Baseline vs Advanced comparative evaluation | [logs/trajectories/traj-08-comparative-evaluation.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-08-comparative-evaluation.json) | `outputs/comparison-results.json` |
| `traj-09-final-review` | `Privacy & Security Reviewer` | Qualification gate audit & security review | [logs/trajectories/traj-09-final-review.json](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-09-final-review.json) | `docs/qualification-gate-checklist.md` |

---

## Tool Disclosure Matrix

| Tool / Agent Name | Purpose & Function | Where Used in Repository | Code / Doc / Test / Asset Generation | Disclosure Mode | Trajectory Retained |
|---|---|---|---|---|---|
| **Antigravity AI (Gemini 3.6 Flash / Pro)** | Primary pair-programming agent & project coordinator | Entire codebase, scripts, specs, and documentation | Generated code (`app/`, `scripts/`, `tests/`), schemas, and docs | Full repository disclosure | Yes (`logs/trajectories/` & `transcript.jsonl`) |
| **Research Subagent** | Codebase inspection & background environment analysis | Local repository workspace discovery | None (read-only research) | Full repository disclosure | Yes |
| **Pillow (PIL)** | Synthetic form image rendering & evidence crop generation | `scripts/generate_synthetic_corpus.py` & `app/backend/agents/quality_agent.py` | Generated synthetic document images (`data/synthetic/`) | Script output disclosure | Yes (`data/manifests/manifest.json`) |
| **FastAPI / Pydantic v2** | Backend REST API server & typed data contract validation | `app/backend/main.py` & `app/shared/schemas.py` | Generated API routes & validation logic | Source code | Yes (`tests/test_api.py`) |
| **Pytest Test Runner** | Automated schema validation & pipeline regression testing | `scripts/run_schema_tests.py` & `tests/` | None (executes unit test suites) | Terminal output | Yes (110/110 PASSED) |

---

## Declaration of Human Oversight
All agent-generated code, schemas, verification rules, evaluation harnesses, and documentation were explicitly requested, reviewed, tested, and approved by the human participant, **Victor Sabo**.
