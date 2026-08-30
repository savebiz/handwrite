# Reusable Skill: Metadata Governance

- **Purpose**: Maintain data contract schemas, field sensitivity levels, and metadata dictionary specifications.
- **Human Approval Boundary**: Sensitivity classifications and data contract changes must be approved by Victor Sabo.
- **Input Files**: `specs/metadata-dictionary.md`, `specs/shared-data-contract.md`
- **Output Files**: `app/shared/metadata.py`, `app/shared/schemas.py`
- **Permitted Actions**: Schema definition, Pydantic model validation, field metadata lookup logic.
- **Prohibited Actions**: Auto-accepting personal PII or sensitive fields without human review sign-off.
- **Tests & Evidence Required**: `python scripts/run_schema_tests.py` (5/5 PASS).
- **Escalation Conditions**: Schema violation, invalid field type, unclassified field.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic anonymized data only.
2. Zero handwriting hallucination.
3. Every field must maintain bounding box evidence coordinates.
4. Keep metadata governance separate from model extraction logic.
5. Apply deterministic validation rules.
6. Enforce mandatory human review for personal and sensitive fields.
7. No external deployment.
8. State only empirical validation evidence.
