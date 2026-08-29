# Specs: Field Inspection Form Family

## Description
Paper forms completed by field inspectors on site (e.g. equipment checks, safety audits).

## Schema Fields
- `inspection_ref` (Required, Pattern `INSP-YYYY-XXX`)
- `inspection_date` (Required, ISO Date)
- `site_location` (Required, Text)
- `inspector_name` (Required, Personal)
- `asset_ref` (Required, Pattern `AST-XXXXX`)
- `inspection_status` (Required, Enum: PASS / FAIL / NEEDS_ATTENTION)
- `observation_finding` (Optional, Text)
- `action_required` (Optional, Text)
- `followup_date` (Optional, ISO Date >= inspection_date)
- `form_completeness` (Required, Enum: COMPLETE / INCOMPLETE)
