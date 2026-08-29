# Specs: Reviewer Decision Policy

- **Triage Thresholds**:
  - `confidence >= 0.85` AND all verification rules `PASS` AND sensitivity `public` / `internal` => `auto_accept`
  - `confidence < 0.85` OR any verification rule `FAIL` OR sensitivity `personal` / `sensitive` => `human_review`
  - `document_quality.status == fail` => `rescan_required`

- **Reviewer Actions**:
  - `approve`: Accept proposed/normalized value as correct.
  - `correct`: Replace value with manual entry (requires `reviewer_reason`).
  - `reject`: Flag value as unreadable or invalid (requires `reviewer_reason`).
  - `rescan`: Reject entire document due to quality issues.

- **Export Governance**: A record state becomes `approved` ONLY when all fields are either `auto_accept` or reviewer-`approved`/`corrected`. No sensitive PII field can be exported without human review sign-off.
