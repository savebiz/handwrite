# HandWrite Verify — Product Roadmap

## P0: Core MVP (Hackathon Focus)
- [x] Repository foundation, operating manuals, and governance documentation.
- [ ] Shared structured data contract (`app/shared/schemas.py`).
- [ ] Metadata dictionary and field sensitivity specifications.
- [ ] Synthetic form generators & 12-document labelled gold evaluation corpus.
- [ ] Simple baseline extractor (single-stage unstructured extraction).
- [ ] Document intake & quality assurance agent (blur, skew, rotation, rescan routing).
- [ ] Document classification agent (`field_inspection` vs `customer_onboarding`).
- [ ] Bounding-box aware field extraction agent with confidence scores.
- [ ] Deterministic verification rules engine (dates, patterns, vocabulary, required fields).
- [ ] Risk-aware triage agent (confidence thresholds, rule checks, sensitivity routing).
- [ ] Interactive reviewer workspace (dual pane: original image/crop viewer + field decision controls).
- [ ] Approved record assembly and structured JSON / CSV exporter.
- [ ] Immutable audit logger (`logs/audit.jsonl`).
- [ ] Automated evaluation harness and comparative results table.
- [ ] Step-by-step clean-environment reproduction guide & 5-minute video plan.

## P1: Enhancements (Post-P0)
- [ ] Batch document processing & queue management.
- [ ] Dynamic user-configurable triage confidence thresholds.
- [ ] Reviewer pattern memory store (anonymized approved extraction corrections).
- [ ] Live evaluation analytics dashboard.
- [ ] Layout-aware template anchor auto-detection.

## Out of Scope
- Training custom proprietary OCR / vision deep learning models from scratch.
- Live production ECM / M-Files repository connectors.
- Real customer paper documents or PII.
- Autonomous approval of sensitive/personal identity fields.
- Legal, health, or financial compliance advice.
