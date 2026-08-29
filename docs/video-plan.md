# Five-Minute Video Presentation & Demo Plan — HandWrite Verify

## Minute 0:00 - 0:45: The Problem & Baseline Bottleneck
- **Problem**: Digitization teams processing paper forms waste manual hours reading handwriting, indexing metadata, and catching bad scans. Unstructured OCR systems output text without visual evidence and silently treat uncertain handwriting as fact.
- **Baseline Demonstration**: Show baseline output misreading hard/blurred handwriting and blindly auto-accepting unverified text.

## Minute 0:45 - 2:00: HandWrite Verify Solution & Architecture
- Introduce HandWrite Verify promise: *"Structured, evidence-linked, review-ready records—without silently treating uncertain handwriting as fact."*
- Walk through multi-stage pipeline: Intake Quality -> Classification -> Extraction -> Deterministic Verification -> Risk-Aware Triage.

## Minute 2:00 - 3:30: Interactive Dual-Pane Reviewer Experience
- Live demo of Reviewer Workspace:
  - Left pane: Original form image + visual crop evidence bounds.
  - Right pane: Extracted values, confidence scores, deterministic rule warnings (`RULE-PAT-003`, `RULE-SENS-006`).
  - Demonstrate mandatory human review guardrail for personal PII fields.
  - Show operator approving and correcting values, updating record status to `approved`.

## Minute 3:30 - 4:30: Evaluation Metrics & Hard Case Reveal
- Present comparative evaluation table:
  - Baseline Accuracy: 83.33% vs Agentic Accuracy: 100.0%
  - Escalation Recall: 100.0%
- Spotlight Hard Case `FI-006` (extreme blur, skew, crossed-out text, missing mandatory inspector name) and explain how Quality Agent routed it to `rescan_required`.

## Minute 4:30 - 5:00: Main Lesson & Practical Takeaway
- Summary: Never treat handwriting models as infallible decision-makers. Use deterministic verification, visual crop evidence, and human review queues for sensitive or low-confidence data.
