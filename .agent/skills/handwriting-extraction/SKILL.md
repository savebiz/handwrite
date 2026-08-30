# Reusable Skill: Handwriting Extraction

- **Purpose**: Transcribe handwritten and printed form fields, assign confidence scores, and derive source visual bounding boxes `[ymin, xmin, ymax, xmax]`.
- **Human Approval Boundary**: Extraction confidence scoring models and crop bounds must be approved by Victor Sabo.
- **Input Files**: `data/synthetic/*`, `app/shared/schemas.py`, `app/shared/metadata.py`
- **Output Files**: `app/backend/agents/extraction_agent.py`
- **Permitted Actions**: Transcription logic, confidence calculation, crop coordinate derivation.
- **Prohibited Actions**: Hallucinating unbacked field values, omitting bounding box crops.
- **Tests & Evidence Required**: `python tests/test_pipeline.py` (4/4 PASS).
- **Escalation Conditions**: Severe image blur, unreadable region, or invalid image path.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic form data only.
2. Zero handwriting hallucination.
3. Visual crop evidence coordinates required for every extracted field.
4. Keep extraction separate from verification, triage, and human review decisions.
5. Deterministic verification rules run before model judgment.
6. Flag low-confidence (<0.85) fields for human review.
7. No external deployment.
8. Empirical evidence required for all accuracy claims.
