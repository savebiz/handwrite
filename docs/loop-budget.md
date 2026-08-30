# Bounded Loop Budget & Evidence Policy — HandWrite Verify

This document specifies the global budget limits, execution safety policies, and evidence schema governing all engineering loops in HandWrite Verify.

---

## 1. Global Loop Budget Limits
| Limit Parameter | Default Value | Hard Boundary Policy |
|---|---|---|
| **Maximum Iterations** | **3 iterations** per ticket | Stop loop immediately if task is unresolved after 3 iterations. Emit escalation report. |
| **Maximum Wall-Clock Duration** | **30 minutes** per ticket | Stop loop immediately if 30 minutes elapse. Emit escalation report. |
| **Dependency Installation Attempt** | **0 unapproved installs** | Immediate hard stop. Requires explicit sign-off from human participant Victor Sabo before running `pip install` or `npm install`. |
| **Fabricated Metrics Prohibition** | **STRICT BLOCK** | Never create dummy or fabricated evaluation metrics to complete a loop. Every claim must be empirically generated. |

---

## 2. Hard Stop & Escalation Conditions
An engineering loop MUST halt immediately and escalate to human participant Victor Sabo if any of the following occur:
1. **Secret Leak / Security Exposure**: API key, token, or credential detected in source code or output logs.
2. **Real PII / Customer Data**: Attempt to process non-synthetic real paper forms or actual identity records.
3. **Destructive Command**: Terminal command threatening workspace loss or environment corruption.
4. **Ambiguous Specification**: Contradictory data contract rules or missing acceptance criteria.
5. **Iteration Cap Exceeded**: Task incomplete after 3 implementation attempts.

---

## 3. Mandatory Evidence Record Schema
Every completed engineering loop must produce a structured evidence record adhering to this JSON schema:

```json
{
  "loop_id": "LOOP-20260830-001",
  "ticket_id": "TICK-001",
  "agent_role": "fullstack-engineer",
  "start_time": "2026-08-30T21:40:00Z",
  "end_time": "2026-08-30T21:55:00Z",
  "files_changed": [
    "app/backend/pipeline.py"
  ],
  "commands_run": [
    "python tests/test_pipeline.py"
  ],
  "test_results": {
    "schema_tests": "5/5 PASS",
    "pipeline_tests": "4/4 PASS",
    "api_tests": "3/3 PASS"
  },
  "evaluation_dataset_version": "v1.0-12doc-synthetic",
  "metrics": {
    "baseline_verified_accuracy_percent": 84.92,
    "agentic_verified_accuracy_percent": 100.0,
    "escalation_recall_percent": 100.0,
    "unnecessary_review_rate_percent": 13.33,
    "agent_avg_duration_seconds": 0.0189
  },
  "human_decision": "APPROVED by Victor Sabo",
  "changelog_entry": "Appended to CHANGELOG.md [1.3.0]",
  "unresolved_risks": []
}
```
