# 5-Minute Video Presentation Script — HandWrite Verify

**Duration**: 4 minutes 45 seconds (Strictly < 5 minutes)
**Presenter**: Victor Sabo
**Submission**: HandWrite Verify — micro1 Agentic Workflows Hackathon 2026

---

## ⏱️ Video Script & Narration Plan

### [00:00 - 00:30] Segment 1: The Problem
* **Visual**: Show physical scanned field inspection report `FI-004_blur_corrupted.png` with severe blur and cut-off text.
* **Narration**: "In safety-critical industries like field inspection and financial onboarding, physical paper forms are scanned and processed every day. But traditional single-pass OCR systems have a dangerous flaw: when handwriting is distorted, blurry, or missing, traditional OCR hallucinates text or silently returns `null` without evidence, quietly exporting false data into production databases. In safety inspections, misreading an equipment pass date or missing an unreadable defect can lead to catastrophic failures."

---

### [00:30 - 01:00] Segment 2: Simple Baseline Demonstration
* **Visual**: Terminal screen running `python scripts/run_baseline_scoring.py`. Show raw OCR output output JSON.
* **Narration**: "Here is our unassisted single-pass baseline (`scripts/run_baseline_scoring.py`). It processes documents in a single pass without pre-screening quality checks or verification rules. On clean forms, it achieves ~85.7% accuracy. But on distorted or blurry forms like `FI-004`, it quietly outputs misread values and exports corrupted records directly into production."

---

### [01:00 - 02:00] Segment 3: Realistic Field-Inspection Execution (5-Stage Pipeline)
* **Visual**: Terminal running `python scripts/run_test_run_suite.py`. Highlight the 5 pipeline stages in real time:
  1. *Intake Quality*: LAPLACIAN BLUR and BORDER CUTOFF flags.
  2. *Schema Extraction*: Zero fabrication transcription with PIL crop image slicing under `outputs/crops/`.
  3. *Deterministic Verification*: 10 rules (`RULE-REQ-001` through `RULE-COMP-011`) checking date formats, pattern matching, and evidence bounding boxes (`RULE-EVID-010`).
  4. *Triage Decision*: Policy table hierarchy evaluating confidence threshold (`0.85`), quality status, and PII sensitivity.
* **Narration**: "To solve this, we built HandWrite Verify: a 5-stage agentic workflow. First, Document Quality pre-screens images using Pillow algorithms—detecting blur and skew before wasting OCR cycles. Second, Schema Extraction transcribes values without inventing missing data, generating physical PNG evidence crops. Third, Deterministic Verification runs 10 strict validation rules. Fourth, Triage Decision applies a strict matrix: confidence under 0.85, failed rules, or sensitive PII mandatory route to human review or rescan."

---

### [02:00 - 03:00] Segment 4: Human Reviewer Interface & Export Guardrails
* **Visual**: Open browser at `http://localhost:8000/static/reviewer.html`.
  1. Show dual-pane workspace: original document image on left, evidence crops (`/crops/AXA-ATT-001_attendee_name.png`) on right.
  2. Show field decisions (`human_review` for sensitive PII field `attendee_name`).
  3. Show reviewer actions: `approved`, `corrected` with **mandatory reason** requirement.
  4. Show export attempt on pending record: Displays red error banner (`HTTP 400: Pending record cannot be exported`).
  5. Submit reviewer correction, transition record to `APPROVED`, then click export.
* **Narration**: "Now let's open the Reviewer Dashboard (`http://localhost:8000/static/reviewer.html`). The reviewer sees the exact visual crop evidence alongside proposed values. Sensitive PII fields are flagged for mandatory human sign-off. If a reviewer attempts to export a pending record or an unapproved sensitive field, our backend blocks export with an HTTP 400 error. Once the reviewer submits a correction with a mandatory reason, the record transitions to APPROVED and exports cleanly with an immutable audit event."

---

### [03:00 - 03:45] Segment 5: Baseline vs. Advanced Comparative Results
* **Visual**: Show comparative evaluation summary screen (`python scripts/run_evaluation.py`) and `outputs/comparison-results.json`.
* **Narration**: "Across our 12-document benchmark corpus (126 fields):
  - Baseline raw accuracy was 85.71%.
  - Our agentic pipeline achieved **99.21% raw accuracy** and **100.00% final reviewer-approved accuracy**.
  - Most importantly, Escalation Recall was **100.00%**—meaning 100% of PII fields, unreadable fields, and quality failures were correctly escalated to human review or rescan."

---

### [03:45 - 04:30] Segment 6: Most Useful Improvement vs. Failed Experiment
* **Visual**: Show code diff for `RULE-EVID-010` crop verification vs unconstrained bounding box experiment log in `CHANGELOG.md`.
* **Narration**: "Our most useful improvement was **Field Evidence Bounding Box Verification (`RULE-EVID-010`)**, which mandates non-zero bounding box coordinates and physical PIL PNG crop generation, guaranteeing 100% visual traceability for audit trails.
  Conversely, an experiment we evaluated was **Unconstrained OCR Bounding Box Rescaling**, which attempted to dynamically expand crop coordinates for skewed images. It caused false-positive crop overlaps on tight multi-line tables, so we removed it."

---

### [04:30 - 04:45] Segment 7: Main Lesson & Conclusion
* **Visual**: Display final architecture slide and GitHub repository URI (`github.com/savebiz/handwrite`).
* **Narration**: "Our main lesson: **Single-pass OCR without agentic quality pre-screening and evidence-linked human triage is a dangerous production liability.** HandWrite Verify ensures high accuracy and 100% audit compliance. Thank you!"
