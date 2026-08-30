# Workflow Ticket 4: Human Reviewer Interface & FastAPI Server

- **Objective**: Build FastAPI application server endpoints and responsive Vite + React dual-pane reviewer workspace.
- **Assigned Virtual Roles**: `fullstack-engineer`, `privacy-security-reviewer`
- **Tasks**:
  1. Build FastAPI REST server (`app/backend/main.py`) with upload, queue, detail, review submission, JSON/CSV export, and evaluation execution endpoints.
  2. Implement export guardrails blocking un-reviewed PII exports with HTTP 400.
  3. Build React SPA (`app/frontend/src/App.jsx`) presenting Dashboard, Upload, Priority Queue, Dual-pane Reviewer Workspace, Approved Record Display, and Evaluation Metrics screens.
- **Definition of Done**:
  - `python tests/test_api.py` passes all API & reviewer workflow checks.
