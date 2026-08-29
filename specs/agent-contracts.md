# Specs: Agent Contracts

## 1. Intake & Quality Agent
- Input: Image file / bytes
- Output: `QualityResult` (status: `pass` | `warning` | `fail`, issues: `list[str]`, `rescan_required`: bool)

## 2. Classification Agent
- Input: Image file, quality result
- Output: `document_type` (`field_inspection` | `customer_onboarding` | `unknown`), confidence float

## 3. Field Extraction Agent
- Input: Image file, schema metadata
- Output: List of proposed values, OCR confidence, and crop coordinates `[ymin, xmin, ymax, xmax]`

## 4. Deterministic Verification Agent
- Input: Field extraction candidates
- Output: List of `VerificationCheck` results per field and normalized values

## 5. Triage Agent
- Input: Extracted candidates, quality result, verification checks, sensitivity flags
- Output: Triage decision per field (`auto_accept` | `human_review` | `rescan_required`) and overall `record_status`
