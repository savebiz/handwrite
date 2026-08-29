# Workflow Ticket 1: Foundation & Schemas

- **Objective**: Create workspace structure, root project documents, typed data contracts, metadata dictionaries, document family schemas, and automated schema validation tests.
- **Assigned Roles**: `information-governance-specialist`, `fullstack-engineer`, `verification-qa-specialist`
- **Tasks**:
  1. Build Python Pydantic models for `DocumentRecord`, `FieldResult`, `QualityResult`, `VerificationCheck`, `AuditEvent` in `app/shared/schemas.py`.
  2. Implement metadata dictionary and field definitions for both document families (`field_inspection` & `customer_onboarding`).
  3. Write unit tests validating valid sample payloads and asserting rejection of malformed or invalid inputs in `tests/test_schemas.py`.
- **Definition of Done**:
  - `pytest tests/test_schemas.py` passes cleanly.
  - Documentation explains field meanings and sensitivity.
