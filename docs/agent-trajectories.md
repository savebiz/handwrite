# Agent Execution Trajectories — HandWrite Verify

This document records representative execution traces for each agent stage across clean, medium, and hard document runs.

---

## Trajectory 1: Intake & Quality Agent
- **Input**: Image file `field_insp_006_extreme.png`
- **Actions**: Contrast variance calculation (`stddev`), edge density analysis, blur marker detection.
- **Output**:
  ```json
  {
    "status": "fail",
    "issues": ["extreme_blur", "skew", "crossed_out_text"],
    "rescan_required": true
  }
  ```
- **Triage Result**: Record status immediately set to `rescan_required`. Prevents unreadable scans from hallucinating field values.

---

## Trajectory 2: Classification Agent
- **Input**: Form image header region
- **Actions**: Layout matching against form header signatures.
- **Output**: `document_type = "customer_onboarding"`, confidence = 0.95.

---

## Trajectory 3: Field Extraction & Evidence Bounding Agent
- **Input**: Form image & field template coordinates
- **Actions**: Crop extraction for `applicant_name`, `contact_number`, `id_ref_placeholder`.
- **Output**: Candidate values linked to visual bounding box coordinates `[ymin, xmin, ymax, xmax]`.

---

## Trajectory 4: Deterministic Verification Agent
- **Input**: Candidate values for `contact_number` = `+14155550192` and `onboarding_ref` = `ONB-2026-101`.
- **Actions**: Execute `RULE-PAT-003` regex checks & `RULE-SENS-006` sensitivity checks.
- **Output**:
  - `onboarding_ref`: `RULE-PAT-003` PASS
  - `contact_number`: `RULE-SENS-006` WARNING (Sensitivity `personal` -> mandatory human review).

---

## Trajectory 5: Human Reviewer Checkpoint
- **Input**: Flagged record `CO-001`
- **Reviewer Action**: Reviewer inspects crop evidence for `applicant_name`, approves proposed value, logs audit event.
- **Output**: Record state updated to `approved`; ready for verified JSON/CSV export.
