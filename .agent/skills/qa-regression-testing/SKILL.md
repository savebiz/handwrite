# Reusable Skill: QA and Regression Testing

- **Purpose**: Execute automated schema validation tests, agent pipeline integration tests, API route tests, and hard-case regression verification.
- **Human Approval Boundary**: All test suite modifications and test pass thresholds must be approved by Victor Sabo.
- **Input Files**: `app/shared/schemas.py`, `app/backend/pipeline.py`, `app/backend/main.py`, `tests/*.py`
- **Output Files**: `scripts/run_schema_tests.py`, `tests/test_schemas.py`, `tests/test_pipeline.py`, `tests/test_api.py`
- **Permitted Actions**: Writing Pytest suites, running test execution scripts, logging test failures.
- **Prohibited Actions**: Deleting or commenting out failing test assertions, using silent try/except blocks to swallow exceptions.
- **Tests & Evidence Required**: `scripts/run_schema_tests.py` (5/5 PASS), `tests/test_pipeline.py` (4/4 PASS), `tests/test_api.py` (3/3 PASS).
- **Escalation Conditions**: Test failure, unhandled traceback, schema violation.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic test data only.
2. Zero handwriting value hallucination in assertions.
3. Require visual crop evidence coordinates `[ymin, xmin, ymax, xmax]` in test payload assertions.
4. Keep QA assertions separate from production triage logic.
5. Apply deterministic validation rules.
6. Verify human review escalation routing for personal PII and corrupt forms.
7. No production deployment.
8. Empirical evidence required for all quality claims.
