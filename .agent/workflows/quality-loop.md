# Workflow Loop C: Quality Loop (Extraction, Validation, Triage & Export Failures)

The **Quality Loop** handles document extraction failures, validation rule errors, improper triage routing, reviewer UI display bugs, and export guardrail violations.

---

## 🔄 7-Phase Execution Sequence
```
PLAN -> IMPLEMENT -> TEST -> INSPECT -> REVIEW -> DOCUMENT -> STOP OR ESCALATE
```

### Phase 1: PLAN
- **Entry Condition**: Bug report, failed integration test, unhandled exception, or export guardrail violation.
- **Required Context**: `CLAUDE.md`, `specs/error-taxonomy.md`, `specs/reviewer-decision-policy.md`, full error traceback logs.
- **Objective**: Identify root cause, fix underlying failure without swallowing exceptions, and verify fix.

### Phase 2: IMPLEMENT
- **Allowed Tools**: `replace_file_content`, `multi_replace_file_content`, `write_to_file`, `view_file`, `grep_search`.
- **Maximum Scope**: `app/backend/agents/*`, `app/backend/pipeline.py`, `app/backend/main.py`, `app/frontend/src/App.jsx`.

### Phase 3: TEST
- **Automated Checks**:
  1. `python tests/test_pipeline.py` (Integration checks, rescan routing, PII mandatory review, typewritten text).
  2. `python tests/test_api.py` (API endpoints, reviewer submission, export guardrails).

### Phase 4: INSPECT
- Verify that error root cause is resolved and zero silent exception fallbacks or dummy data returns were introduced.

### Phase 5: REVIEW
- Audit safety compliance: Ensure personal PII and low-confidence fields remain routed to human review.
- **Human Checkpoint**: Require approval from Victor Sabo if altering error taxonomy classifications or export status enums.

### Phase 6: DOCUMENT
- Update `CHANGELOG.md` with bug fix summary, root cause, and test evidence.
- Emit completed agent handoff record using `docs/agent-handoff-template.md`.

### Phase 7: STOP OR ESCALATE
- **Budget Limits**: Max 3 iterations, max 30 minutes wall-clock.
- **Stop Conditions**: Unresolved traceback, symptom patching without root cause fix, secret leak, or >3 iterations.
- **Escalation Output**: Write escalation note in `logs/` and stop execution.
