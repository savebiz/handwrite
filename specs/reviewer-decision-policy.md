# Specs: Reviewer Decision Policy

- **Triage Thresholds**:
  - `confidence >= 0.85` AND all verification rules `PASS` AND sensitivity `public` / `internal` => `auto_accept`
  - `confidence < 0.85` OR any verification rule `FAIL` OR sensitivity `personal` / `sensitive` => `human_review`
  - `document_quality.status == fail` => `rescan_required`

- **Reviewer Decision States** (per-field `reviewer_decision` enum):
  - `approved`: Accept proposed/normalized value as correct.
  - `corrected`: Replace value with manual entry (requires `reviewer_reason`).
  - `rejected`: Flag value as unreadable or invalid (requires `reviewer_reason`).
  - `pending`: Awaiting human review (initial state for `human_review` fields).
  - `not_required`: No human review needed (initial state for `auto_accept` fields).

- **Document-Level Rescan**: When a reviewer determines the entire document is unusable, the `record_status` is set to `rescan_required`. Rescan is NOT a per-field reviewer decision — it applies at the document level via `record_status`.

- **Export Governance**: A record state becomes `approved` ONLY when all fields are either `auto_accept` (with `reviewer_decision = not_required`) or reviewer-`approved`/`corrected`. No sensitive PII field can be exported without human review sign-off.
