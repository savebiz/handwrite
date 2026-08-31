# Agent Trajectory Index — HandWrite Verify

This document indexes all representative, evidence-backed agent trajectory files stored in `logs/trajectories/`.

---

## 📌 Trajectory Catalog

| Trajectory ID | Agent / Specialist Role | Primary Task | Output Artifact / Evidence Location | Status |
|---|---|---|---|---|
| [traj-01-planning-orchestration](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-01-planning-orchestration.json) | `Project Coordination Lead` | Workspace discovery, roadmap planning, task tracking | `walkthrough.md` | Active |
| [traj-02-baseline-extraction](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-02-baseline-extraction.json) | `Baseline Extraction Runner` | Single-pass baseline extraction across corpus | `outputs/baseline-results.json` | Active |
| [traj-03-intake-quality](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-03-intake-quality.json) | `Document Quality Specialist` | 9 PIL pre-screening quality checks (blur, skew, cutoff) | `scripts/run_intake_quality_tests.py` | Active |
| [traj-04-schema-extraction](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-04-schema-extraction.json) | `Handwriting Extraction Specialist` | Schema-guided extraction & crop PNG generation | `scripts/run_extraction_tests.py` | Active |
| [traj-05-deterministic-verification](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-05-deterministic-verification.json) | `Verification & Triage Specialist` | 10 deterministic rules (`RULE-REQ-001` to `RULE-COMP-011`) | `scripts/run_verification_tests.py` | Active |
| [traj-06-triage-decision](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-06-triage-decision.json) | `Triage & Decision Agent` | Decision table policy hierarchy & record status resolution | `scripts/run_triage_tests.py` | Active |
| [traj-07-reviewer-workflow](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-07-reviewer-workflow.json) | `Reviewer Experience Specialist` | Human review actions, reason enforcement, sensitive export guardrail | `scripts/run_reviewer_tests.py` | Active |
| [traj-08-comparative-evaluation](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-08-comparative-evaluation.json) | `Evaluation Benchmark Specialist` | Baseline vs Advanced comparative evaluation harness | `outputs/comparison-results.json` | Active |
| [traj-09-final-review](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/logs/trajectories/traj-09-final-review.json) | `Privacy & Security Reviewer` | Qualification gate audit & security compliance check | `docs/qualification-gate-checklist.md` | Active |

---

## 🏷️ Role Usage Mapping

### Active Roles
1. **`Project Coordination Lead`** (`.agent/roles/project-coordination-lead.md`): Used for roadmap planning, task decomposition, and milestone execution tracking (`traj-01`).
2. **`Product Workflow Analyst`** (`.agent/roles/product-workflow-analyst.md`): Used for user journey mapping, reviewer requirements, and spec definition (`traj-01`).
3. **`Handwriting Extraction Specialist`** (`.agent/roles/handwriting-extraction-specialist.md`): Used for schema-guided field extraction and crop slicing (`traj-04`).
4. **`Verification & Triage Specialist`** (`.agent/roles/verification-triage-specialist.md`): Used for rule engineering (`RULE-REQ-001` through `RULE-COMP-011`) and decision matrix resolution (`traj-05`, `traj-06`).
5. **`Fullstack Engineer`** (`.agent/roles/fullstack-engineer.md`): Used for FastAPI REST API endpoints and static reviewer UI dashboard (`traj-07`).
6. **`QA & Reliability Specialist`** (`.agent/roles/qa-reliability-specialist.md`): Used for test suite generation (`tests/`) and standalone test runners (`traj-08`).
7. **`Evaluation & Benchmark Specialist`** (`.agent/roles/evaluation-benchmark-specialist.md`): Used for comparative benchmark scoring and error analysis (`traj-08`).
8. **`Privacy & Security Reviewer`** (`.agent/roles/privacy-security-reviewer.md`): Used for sensitive field export guardrails and qualification gate compliance (`traj-09`).

### Defined but Not Used
1. **`Information Governance Specialist`** (`.agent/roles/information-governance-specialist.md`): Defined during initial setup; merged into `Privacy & Security Reviewer` during implementation.
2. **`Reproducibility & Submission Editor`** (`.agent/roles/reproducibility-submission-editor.md`): Defined during initial setup; merged into `Evaluation Benchmark Specialist` and `Project Coordination Lead`.

---

## 🛡️ Privacy & Zero-Secrets Compliance Statement
All trajectory JSON files stored in `logs/trajectories/` have been audited and verified:
- **Zero API Keys or Credentials**: No OpenAI, Gemini, or Anthropic API keys or secrets are stored.
- **Zero Real Personal Data**: All evaluated documents use 100% synthetic mock handwriting data (`data/synthetic/`).
- **Immutable Audit Trails**: Reviewer actions and pipeline executions log structured, privacy-safe audit events.
