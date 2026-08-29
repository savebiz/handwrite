# Specs: Deterministic Verification Rules

1. **`RULE-REQ-001` (Required Field Check)**: If field is required and proposed value is null or empty string -> `FAIL`.
2. **`RULE-DATE-002` (ISO Date Validation)**: Parse proposed string as ISO date (`YYYY-MM-DD`). If invalid -> `FAIL`. If date > current date -> `FAIL`.
3. **`RULE-PAT-003` (Pattern Match)**: Test against field regex (e.g. `INSP-\d{4}-\d{3}`). If mismatch -> `FAIL`.
4. **`RULE-VOCAB-004` (Controlled Vocabulary)**: Check against allowed enums. If not in vocabulary -> `FAIL`.
5. **`RULE-CROSS-005` (Followup Date Check)**: If `followup_date` < `inspection_date` -> `FAIL`.
6. **`RULE-SENS-006` (Sensitivity Guardrail)**: If field sensitivity is `personal` or `sensitive` -> Force decision to `human_review`.
