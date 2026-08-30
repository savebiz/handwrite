# HandWrite Verify — Product Roadmap & Execution Priorities

## 🎯 Engineering Priority Order
1. **Agent Solution Engineering**: Multi-stage quality, classification, extraction, verification, and triage architecture.
2. **Reproducibility**: Programmatic synthetic corpus generation, clean setup, and automated evaluation harness.
3. **Measured Improvement**: Baseline vs Agentic Pipeline comparative metrics on Verified Field Accuracy.
4. **End-to-End Quality**: Robust deterministic validation rules, evidence crop links, and export safety guardrails.
5. **Visual Polish**: Responsive dual-pane reviewer workspace.

---

## 📋 Document Schema Scope
- **Primary Demo Schema**: `field_inspection` forms (equipment checks, site findings, action items).
- **Secondary Supported Schema**: `customer-onboarding` forms (applications, contact info, PII guardrails).

---

## P0: Core MVP (Completed)
- [x] Repository foundation, operating manuals, and governance documentation.
- [x] Shared structured data contract (`app/shared/schemas.py`).
- [x] Metadata dictionary and field sensitivity specifications (`app/shared/metadata.py`).
- [x] Programmatic synthetic form generator & 12-document labelled gold evaluation corpus (`scripts/generate_synthetic_corpus.py`).
- [x] Single-pass baseline extractor (`evaluation/baseline.py`).
- [x] Document intake & quality assurance agent (`app/backend/agents/quality_agent.py`).
- [x] Document classification agent (`app/backend/agents/classification_agent.py`).
- [x] Bounding-box aware field extraction agent (`app/backend/agents/extraction_agent.py`).
- [x] Deterministic verification rules engine (`app/backend/agents/verification_agent.py`).
- [x] Risk-aware triage agent (`app/backend/agents/triage_agent.py`).
- [x] Interactive dual-pane reviewer workspace SPA (`app/frontend/src/App.jsx`).
- [x] Approved record assembly and structured JSON / CSV exporter (`app/backend/main.py`).
- [x] Append-only audit logger (`app/backend/audit.py`).
- [x] Automated comparative evaluation harness (`evaluation/evaluate.py`).
- [x] Step-by-step clean-environment reproduction guide & 5-minute video plan (`docs/reproduction.md`, `docs/video-plan.md`).

---

## ⏸️ Deferred / Out of Scope
- Training custom proprietary OCR / handwriting neural network models from scratch.
- Live production ECM or M-Files repository connectors.
- Real customer paper documents or real PII.
- Production deployment or multi-user authentication infrastructure.
- Batch processing and background queue management.
- Complex analytics dashboards.
- Pattern memory stores (deferred unless post-P0 production enhancements are requested).
- Autonomous approval of sensitive/personal identity fields.
- Legal, health, or financial compliance advice.
