# Reusable Skill: Full-Stack Delivery

- **Purpose**: Implement backend FastAPI API server endpoints, React SPA reviewer interface, and verified record exporters.
- **Human Approval Boundary**: Public API routes and frontend build architecture must be approved by Victor Sabo.
- **Input Files**: `specs/api-contracts.md`, `specs/shared-data-contract.md`
- **Output Files**: `app/backend/main.py`, `app/frontend/src/App.jsx`, `api/index.py`, `pyproject.toml`, `vercel.json`
- **Permitted Actions**: Writing API routes, building frontend SPA views, enforcing export security guardrails.
- **Prohibited Actions**: Bypassing PII export guardrails, installing unapproved third-party dependencies.
- **Tests & Evidence Required**: `python tests/test_api.py` (3/3 PASS).
- **Escalation Conditions**: Unhandled backend exception, API contract breaking change, export guardrail failure.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic evaluation data only.
2. Zero handwriting hallucination.
3. Display visual bounding box crop evidence in dual-pane reviewer workspace.
4. Maintain strict separation of backend API from frontend UI state.
5. Apply deterministic validation rules.
6. Enforce human review sign-off for personal/sensitive fields before allowing record export.
7. No external deployment.
8. State only empirical test evidence.
