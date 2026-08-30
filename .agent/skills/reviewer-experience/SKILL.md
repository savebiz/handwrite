# Reusable Skill: Reviewer Experience

- **Purpose**: Build responsive dual-pane reviewer interface displaying original form image, side-by-side field evidence crops, confidence badges, and review action controls.
- **Human Approval Boundary**: UI design layout and reviewer decision controls must be approved by Victor Sabo.
- **Input Files**: `specs/api-contracts.md`, `specs/shared-data-contract.md`
- **Output Files**: `app/frontend/src/App.jsx`, `app/frontend/index.html`
- **Permitted Actions**: Building React components, crop canvas rendering, status badge styling.
- **Prohibited Actions**: Allowing reviewer UI to bypass backend PII export guardrails.
- **Tests & Evidence Required**: `python tests/test_api.py` (End-to-End Human Review Test PASS).
- **Escalation Conditions**: UI rendering error, missing image crop path, unhandled API error.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic evaluation forms only.
2. Zero handwriting hallucination in UI state.
3. Display visual bounding box crop evidence in dual-pane reviewer workspace.
4. Maintain strict separation of UI presentation from backend triage logic.
5. Apply deterministic validation rules.
6. Require explicit human reviewer sign-off for personal/sensitive fields.
7. No external deployment.
8. State only empirical test evidence.
