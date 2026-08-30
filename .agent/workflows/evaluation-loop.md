# Workflow Loop B: Evaluation Loop (Baseline & Agent Benchmark Changes)

The **Evaluation Loop** governs any modification to the baseline extractor, extraction agent, quality agent, verification rules, or comparative evaluation harness.

---

## 🔄 7-Phase Execution Sequence
```
PLAN -> IMPLEMENT -> TEST -> INSPECT -> REVIEW -> DOCUMENT -> STOP OR ESCALATE
```

### Phase 1: PLAN
- **Entry Condition**: Modification to OCR extraction, quality scoring, verification rules, or evaluation scripts.
- **Required Context**: `CLAUDE.md`, `specs/evaluation-plan.md`, `data/manifests/manifest.json`, `evaluation/evaluate.py`.
- **Objective**: Improve or verify field extraction accuracy against identical labelled synthetic benchmark corpus.

### Phase 2: IMPLEMENT
- **Allowed Tools**: `replace_file_content`, `multi_replace_file_content`, `write_to_file`, `view_file`, `run_command`.
- **Maximum Scope**: `app/backend/agents/*`, `evaluation/*`, `scripts/generate_synthetic_corpus.py`.

### Phase 3: TEST
- **Automated Checks**:
  1. `python scripts/generate_synthetic_corpus.py` (Regenerates 12 synthetic document forms).
  2. `python evaluation/evaluate.py` (Executes baseline vs agent comparative evaluation harness).

### Phase 4: INSPECT
- Read empirical metric outputs in `outputs/evaluation_results.json`.
- Verify Verified Field Accuracy, Escalation Recall (100% target), and Unnecessary Review Rate without fabricated metrics.

### Phase 5: REVIEW
- Compare results against previous run recorded in `outputs/evaluation_results.json`.
- **Human Checkpoint**: Require approval from Victor Sabo before accepting changed baseline algorithms or confidence thresholds.

### Phase 6: DOCUMENT
- Update `outputs/evaluation_results.json` and `CHANGELOG.md` with empirical benchmark results.
- Emit completed agent handoff record using `docs/agent-handoff-template.md`.

### Phase 7: STOP OR ESCALATE
- **Budget Limits**: Max 3 iterations, max 30 minutes wall-clock.
- **Stop Conditions**: Accuracy degradation, fabricated data attempt, corrupted gold labels, or >3 iterations.
- **Escalation Output**: Write escalation note in `logs/` and stop execution.
