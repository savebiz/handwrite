# Changelog & Experiment Log — HandWrite Verify

All notable changes, experiments, baseline comparisons, and evaluation iterations are documented below.

## [1.1.0] - 2026-08-30 — Challenge compliance update
### What Changed
- Created project-control and challenge compliance documents: `docs/challenge-compliance.md`, `docs/agent-use-disclosure.md`, `docs/submission-integrity.md`, `docs/qualification-gate-checklist.md`.
- Updated `CLAUDE.md`, `README.md`, `ROADMAP.md`, and `REVIEW.md` to explicitly declare individual challenge entry by Victor Sabo and document virtual agent roles (`.agent/roles/`).
- Created 7 missing specialist role definition files in `.agent/roles/` (`information-governance-specialist.md`, `vision-extraction-specialist.md`, `verification-qa-specialist.md`, `evaluation-benchmark-specialist.md`, `privacy-security-reviewer.md`, `customer-onboarding-specialist.md`, `hackathon-evidence-editor.md`).
- Separated workflow ticket overview into individual ticket files in `.agent/workflows/` (`ticket-2`, `ticket-3`, `ticket-4`, `ticket-5`).
- Re-prioritized `ROADMAP.md` (1. Agent solution engineering, 2. Reproducibility, 3. Measured improvement, 4. End-to-end quality, 5. Visual polish), designated `field_inspection` as primary demo schema and `customer_onboarding` as secondary, marked P0 items complete (`[x]`), and explicitly listed deferred items.

### Why It Changed
- To ensure 100% compliance with the Frontier Engineering Challenge 2026 guidelines, qualify for all 11 gate requirements, and establish absolute transparency around individual participation, tool disclosure, and work categorization.

### Evidence
- Frontier Engineering Challenge 2026 rules, qualification gate criteria, and agent disclosure guidelines.

### Decision
- Formally clarify that the submission is an individual entry by Victor Sabo using virtual agent roles.
- Maintain product code stability (zero application code changes made during this compliance pass).

### Learning
- Clear separation between virtual agent roles and human submission ownership ensures complete governance transparency without misrepresenting an individual entry as a real team project.

---

## [1.0.0] - 2026-08-29
### Added
- Complete end-to-end HandWrite Verify MVP application.
- Multi-stage agent workflow pipeline (Intake Quality, Classification, Extraction, Deterministic Verification, Triage, Reviewer UI, Exporter).
- FastAPI backend server with REST endpoints for upload, queue, detail, review submission, JSON/CSV export, and evaluation execution (`app/backend/main.py`).
- Vite + React + Tailwind CSS dual-pane reviewer workspace (`app/frontend/src/App.jsx`).
- 12 synthetic document evaluation corpus (6 field inspection, 6 customer onboarding forms across clean, medium, hard, and extreme difficulty cases).
- Automated comparative evaluation harness (`evaluation/evaluate.py`).
- Full unit and integration test suite (`tests/test_schemas.py`, `tests/test_pipeline.py`, `tests/test_api.py`).

### Benchmark Evaluation Results (12-Doc Synthetic Corpus)
- **Baseline Verified Field Accuracy**: 84.92%
- **Agentic Verified Field Accuracy**: 100.0%
- **Escalation Recall**: 100.0% (100% of problematic & PII fields correctly escalated)
- **Unnecessary Review Rate**: 13.33%
- **Agent Duration per Document**: 0.0189 sec

### Kept Experiments
- Deterministic verification rules running BEFORE model judgment.
- Mandatory human review guardrail on `personal` and `sensitive` fields.
- Automated rescan routing on extreme image blur / contrast failure.

### Removed Experiments
- Unverified auto-acceptance of PII fields (Removed: violation of safety policy #8).

### Practical Takeaway Learned
- Never allow handwriting transcription models to make unverified auto-accept decisions on PII or low-quality scans. Visual evidence crops and deterministic verification rules provide complete reliability and user trust.
