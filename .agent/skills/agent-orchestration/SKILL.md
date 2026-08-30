# Reusable Skill: Agent Orchestration

- **Purpose**: Coordinate multi-stage agentic workflow execution (Intake Quality -> Classification -> Extraction -> Verification -> Triage -> Audit Logging).
- **Human Approval Boundary**: Pipeline architecture and stage ordering must be approved by Victor Sabo.
- **Input Files**: `app/shared/schemas.py`, `app/backend/agents/*.py`
- **Output Files**: `app/backend/pipeline.py`
- **Permitted Actions**: Pipeline orchestration logic, error propagation, document status routing.
- **Prohibited Actions**: Bypassing processing stages or suppressing agent errors.
- **Tests & Evidence Required**: `python tests/test_pipeline.py` (4/4 PASS).
- **Escalation Conditions**: Pipeline stage failure, unhandled exception, corrupt document.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic evaluation inputs only.
2. Zero handwriting hallucination.
3. Every candidate field retains visual crop evidence coordinates.
4. Maintain strict separation of processing stages.
5. Deterministic rule validation BEFORE model judgment.
6. Route low-confidence, contradictory, or PII fields to human review.
7. No external deployment.
8. State only empirical test evidence.
