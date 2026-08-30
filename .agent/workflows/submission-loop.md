# Workflow Loop D: Submission Loop (Submission Verification & Readiness)

The **Submission Loop** governs clean-environment reproduction verification, documentation integrity, agent trajectory audit, video plan readiness, and qualification-gate compliance.

---

## 🔄 7-Phase Execution Sequence
```
PLAN -> IMPLEMENT -> TEST -> INSPECT -> REVIEW -> DOCUMENT -> STOP OR ESCALATE
```

### Phase 1: PLAN
- **Entry Condition**: Final submission audit pass prior to hackathon deadline or milestone release.
- **Required Context**: `CLAUDE.md`, `ROADMAP.md`, `REVIEW.md`, `docs/challenge-compliance.md`, `docs/qualification-gate-checklist.md`, `docs/agent-use-disclosure.md`, `docs/submission-integrity.md`.
- **Objective**: Verify 100% submission readiness, clean reproducibility, valid documentation links, and complete qualification gate compliance.

### Phase 2: IMPLEMENT
- **Allowed Tools**: `view_file`, `write_to_file`, `replace_file_content`, `run_command`.
- **Maximum Scope**: Documentation (`docs/*`, `README.md`, `CHANGELOG.md`, `pyproject.toml`, `vercel.json`). Zero product application code edits allowed.

### Phase 3: TEST
- **Automated Checks**:
  1. `python scripts/run_schema_tests.py` (5/5 PASS)
  2. `python tests/test_pipeline.py` (4/4 PASS)
  3. `python tests/test_api.py` (3/3 PASS)
  4. `python evaluation/evaluate.py` (Comparative benchmark execution)
  5. `git status` (Clean working tree check)

### Phase 4: INSPECT
- Audit 11 qualification gate criteria in `docs/qualification-gate-checklist.md`.
- Verify all file links use markdown `file://` format and resolve cleanly.

### Phase 5: REVIEW
- **Human Checkpoint**: Require final review and submission approval from human participant **Victor Sabo**.

### Phase 6: DOCUMENT
- Update `CHANGELOG.md` with milestone release entry.
- Emit completed submission handoff record using `docs/agent-handoff-template.md`.

### Phase 7: STOP OR ESCALATE
- **Budget Limits**: Max 3 iterations, max 30 minutes wall-clock.
- **Stop Conditions**: Failing test, un-tracked file, unbacked performance claim, or missing qualification item.
- **Escalation Output**: Write escalation note in `logs/` and stop execution.
