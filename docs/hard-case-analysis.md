# Extreme Hard Case Analysis — Sample FI-006

## 1. Document Characteristics
- **Document ID**: `FI-006` (`field_insp_006_extreme.png`)
- **Document Family**: `field_inspection`
- **Flaws Included**:
  1. Extreme image blur (Gaussian blur radius > 3.0).
  2. Document skew (rotational offset > 6 degrees).
  3. Crossed-out handwriting text (`120psi` crossed out with red strikethrough -> `80psi`).
  4. Missing mandatory field (`inspector_name` left blank).
  5. Multiple handwriting styles across inspector notes.

---

## 2. Baseline Performance vs Agentic Pipeline

### Baseline Behavior
- The baseline extractor attempted single-pass OCR on the blurred image.
- It misread the crossed-out text as literal fact without detecting strikethrough marks.
- It auto-accepted the record with an empty `inspector_name` field.
- **Outcome**: Produced corrupted, unverified output record.

### Agentic Pipeline Behavior
1. **Intake & Quality Agent**: Instantly detected `extreme_blur` and contrast degradation. Set `document_quality.status = fail` and `rescan_required = True`.
2. **Deterministic Verification Agent**: Triggered `RULE-REQ-001` failure on missing mandatory `inspector_name`.
3. **Triage Agent**: Routed the document to `rescan_required` queue.
4. **Human Reviewer Interface**: Displayed clear visual warning: *"Document quality check failed — extreme blur & missing mandatory field"*.

---

## 3. Key Lesson Learned
An agentic document system MUST establish a hard quality firewall. Attempting OCR on unreadable, blurred, or corrupt scans produces silent hallucinations. Routing severe image flaws to `rescan_required` protects downstream business systems from corrupted metadata.
