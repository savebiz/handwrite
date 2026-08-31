# Known Technical Limitations & Failure Mode Analysis — HandWrite Verify

This document explicitly details all current technical limitations, system trade-offs, and edge-case failure modes in HandWrite Verify.

---

## 1. Primary Technical Limitations

### 1. Local PIL Image Crop Fallback
- **Limitation**: When commercial visual language model (VLM) vision endpoints are unconfigured or offline, extraction falls back to deterministic local PIL image slicing based on schema bounding box templates.
- **Trade-off**: Guarantees 100% offline reproducibility and $0.00 cloud costs, but relies on predictable handwriting alignment within predefined schema bounding box coordinates.

### 2. Static Bounding Box Templates
- **Limitation**: Bounding box coordinates (`ymin, xmin, ymax, xmax`) in `app/shared/metadata.py` are configured per document schema type.
- **Trade-off**: Highly efficient for standard form templates, but requires explicit schema template configuration when introducing entirely new physical document layouts.

### 3. Reviewer Web UI Local Database
- **Limitation**: The reviewer web application (`app/static/reviewer.html`) interacts with a local file-backed JSON database store (`outputs/db/`).
- **Trade-off**: Simplifies local setup without requiring a dedicated PostgreSQL/MongoDB instance, but requires persistent disk volume mounts when deployed to cloud serverless environments.

---

## 2. Detailed Failure Mode Analysis

### ⚠️ Primary Failure Mode: Severe Image Rotation & Extreme Skew (> 30°)
- **Root Cause**: When a scanned physical document is rotated beyond 30° without physical image de-skewing pre-processing, target handwriting text shifts outside default schema bounding box regions.
- **Symptom**: PIL crop slicing generates zero-area or misaligned PNG crop images (`[0, 0, 0, 0]`).
- **Pipeline Mitigation**:
  1. *Stage 1 (Intake Quality)*: The `row_projection_skew` check detects extreme skew during pre-screening.
  2. *Quality Routing*: Quality status transitions to `FAIL` and `rescan_required = True`.
  3. *Stage 3 (Verification)*: Rule `RULE-EVID-010` fails on zero-area bounding boxes.
  4. *Stage 4 (Triage)*: Decision table hierarchy forces document record status to `RESCAN_REQUIRED`, preventing unverified corrupted fields from auto-accepting or exporting.

---

## 3. Future Engineering Roadmap

1. **Dynamic OCR Bounding Box Re-Alignment**: Implement dynamic bounding box text-detector (e.g. CRAFT / DBNet) to adjust crop coordinates dynamically for rotated forms.
2. **PostgreSQL Audit DB Adapter**: Replace local file-backed JSON DB with PostgreSQL + PGVector for scalable enterprise deployments.
3. **Calibrated Confidence Ensemble**: Blend visual OCR confidence with language model perplexity to refine auto-accept thresholding.
