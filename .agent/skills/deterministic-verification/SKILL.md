# Reusable Skill: Deterministic Verification

- **Purpose**: Execute rule-based checks (ISO dates, regex patterns, enums, required fields, cross-field checks) prior to model judgment.
- **Human Approval Boundary**: Verification rules and failure policies must be approved by Victor Sabo.
- **Input Files**: `specs/verification-rules.md`, `app/shared/metadata.py`
- **Output Files**: `app/backend/agents/verification_agent.py`
- **Permitted Actions**: Regex pattern checks, date validation, enum lookup, required field validation.
- **Prohibited Actions**: Auto-accepting failed rule checks or bypassing rule errors.
- **Tests & Evidence Required**: `python tests/test_pipeline.py` (4/4 PASS).
- **Escalation Conditions**: Rule failure, invalid date string, pattern mismatch.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic data only.
2. Zero handwriting hallucination.
3. Every verified field retains visual crop evidence coordinates.
4. Separate deterministic verification from downstream human review decisions.
5. Execute deterministic checks BEFORE model judgment.
6. Route rule failures to human review.
7. No external deployment.
8. State only empirical test evidence.
