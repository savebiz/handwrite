# Workflow Ticket 3: Agent Workflow Backend

- **Objective**: Implement the multi-stage agentic processing pipeline (Intake Quality, Classification, Extraction, Deterministic Verification, Triage, and Audit Logging).
- **Assigned Virtual Roles**: `vision-extraction-specialist`, `verification-qa-specialist`, `information-governance-specialist`
- **Tasks**:
  1. Build Intake & Quality Agent (`quality_agent.py`) for blur/skew/contrast analysis and `rescan_required` firewall.
  2. Build Classification Agent (`classification_agent.py`) for template category routing.
  3. Build Extraction Agent (`extraction_agent.py`) with bounding box crop coordinates `[ymin, xmin, ymax, xmax]` and confidence scoring.
  4. Build Deterministic Verification Agent (`verification_agent.py`) for regex, ISO date, enum, required, and cross-field checks.
  5. Build Triage Agent (`triage_agent.py`) enforcing mandatory human review for personal PII fields.
  6. Build Audit Logger (`audit.py`) writing append-only logs to `logs/audit.jsonl`.
- **Definition of Done**:
  - `python tests/test_pipeline.py` passes 100% of integration checks.
