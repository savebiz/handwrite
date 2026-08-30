# Workflow Loop A: Ticket Loop (Small Implementation Tasks)

The **Ticket Loop** governs small, focused implementation tasks (e.g., bug fixes, UI adjustments, rule additions, schema updates).

---

## 🔄 7-Phase Execution Sequence
```
PLAN -> IMPLEMENT -> TEST -> INSPECT -> REVIEW -> DOCUMENT -> STOP OR ESCALATE
```

### Phase 1: PLAN
- **Entry Condition**: Assigned ticket or user request for a small code/doc change.
- **Required Context**: `CLAUDE.md`, `ROADMAP.md`, `specs/shared-data-contract.md`, assigned role definition (`.agent/roles/`), assigned skill (`.agent/skills/`).
- **Objective**: Formulate explicit edit plan, target files, acceptance criteria, and risks.

### Phase 2: IMPLEMENT
- **Allowed Tools**: `replace_file_content`, `multi_replace_file_content`, `write_to_file`, `view_file`, `list_dir`, `grep_search`.
- **Maximum Scope**: Focused single component or module (max 3 files).

### Phase 3: TEST
- **Automated Checks**: `python scripts/run_schema_tests.py` and unit/integration test runners (`tests/`).

### Phase 4: INSPECT
- Inspect stdout, stderr, and test outputs. Verify zero unhandled exceptions or broken contracts.

### Phase 5: REVIEW
- Audit changes against 14-point review checklist in `REVIEW.md`.
- **Human Checkpoint**: Require approval from Victor Sabo for public API changes, schema changes, or dependency additions.

### Phase 6: DOCUMENT
- Emit completed agent handoff record using `docs/agent-handoff-template.md`.
- **Changelog Requirement**: Append entry to `CHANGELOG.md` if user-facing behavior or contracts changed.

### Phase 7: STOP OR ESCALATE
- **Budget Limits**: Max 3 iterations, max 30 minutes wall-clock.
- **Stop Conditions**: Secrets, real customer data, destructive command, ambiguous spec, or >3 iterations.
- **Escalation Output**: Log escalation report to `logs/` and stop execution.
