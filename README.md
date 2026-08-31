# HandWrite Verify

> **HandWrite Verify turns scanned handwritten business forms into structured, evidence-linked, review-ready records—without silently treating uncertain handwriting as fact.**

---

## 👤 Individual Challenge Submission
* **Participant**: **Victor Sabo** (`sabo.victor1@gmail.com`)
* **Event**: Frontier Engineering Challenge 2026 / micro1 Agentic Workflows Hackathon
* **Submission Type**: Individual Entry. Specialized role definition files (`.agent/roles/`) represent virtual coding-agent roles operated under Victor Sabo's direction.

---

## 📌 Primary & Secondary Document Schemas
* **Primary Demo Schema**: `field_inspection` forms (equipment checks, site locations, inspector observations).
* **Secondary Supported Schema**: `customer-onboarding` forms (applications, contact numbers, PII sensitivity guardrails).

---

## 📁 Work Categorization (Pre-existing vs Challenge-Created)
* **Pre-existing Repository Files**: *None*. The workspace was empty prior to challenge initialization.
* **Challenge-Created Code**: FastAPI backend (`app/backend/`), React SPA (`app/frontend/`), Pydantic schemas (`app/shared/`), evaluation suite (`evaluation/`).
* **Challenge-Created Specs**: 14 specification documents in `specs/`, agent skills in `.agent/skills/`, virtual roles in `.agent/roles/`.
* **Generated Data & Outputs**: 12 synthetic document forms (`data/synthetic/`), gold labels (`data/gold-labels/`), evaluation results (`outputs/evaluation_results.json`).

---

## 🛠️ Tech Stack & Architecture
- **Backend**: Python 3.13 + FastAPI + Pydantic v2 + Pillow
- **Frontend**: Vite + React + Tailwind CSS
- **Deployment**: Vercel Serverless + Static Build Configuration (`vercel.json`, `pyproject.toml`)
- **Data & Logs**: JSON File DB + Append-only Audit Log (`logs/audit.jsonl`)
- **Evaluation Engine**: Automated comparative scoring harness (`evaluation/evaluate.py`)

---

## 🚀 Quickstart & Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure Environment
cp .env.example .env

# 3. Generate 12 Synthetic Evaluation Forms
python scripts/generate_synthetic_corpus.py

# 4. Run Baseline Scoring & Full Test Suite
python scripts/run_test_run_suite.py   # Unified test harness (baseline, advanced, comparison, walkthrough)
python scripts/run_reviewer_tests.py    # Human reviewer workflow tests (9/9 PASS)
python scripts/run_triage_tests.py      # Triage & decision table tests (10/10 PASS)
python scripts/run_verification_tests.py# Deterministic verification tests (14/14 PASS)
python scripts/run_extraction_tests.py  # Schema-guided extraction tests (13/13 PASS)
python scripts/run_intake_quality_tests.py # Enhanced intake quality tests (14/14 PASS)
python -m pytest                         # Full Pytest suite (110/110 PASS)

# 5. Run FastAPI Backend & Reviewer UI Dashboard
uvicorn app.backend.main:app --reload --port 8000
# Reviewer Web UI: http://localhost:8000/static/reviewer.html
```

---

## 🖥️ Human Reviewer Workflow & Export Guardrails

The reviewer workspace (`http://localhost:8000/static/reviewer.html`) provides a human-in-the-loop review UI:
- **Evidence-Linked Inspection**: Displays original document image, crop thumbnail URI (`/crops/{doc_id}_{field_name}.png`), proposed vs normalized values, confidence score, verification checks, decision rationale, and sensitivity tags.
- **Reviewer Actions**:
  - `approved`: 1-click approval for clean fields.
  - `corrected`: Manual value entry with **mandatory** reviewer reason (`reviewer_reason`).
  - `rejected`: Field rejection with **mandatory** reviewer reason.
  - `rescan`: Document-level rescan request with **mandatory** reviewer reason.
- **Export Safety Guardrails**:
  - **Pending Record Export Blocking**: Records in `AWAITING_REVIEW`, `PROCESSING`, or `RESCAN_REQUIRED` status cannot be exported (HTTP 400).
  - **Sensitive PII Export Guardrail**: Records containing `personal` or `sensitive` fields CANNOT be exported unless every sensitive field has received explicit human approval (`APPROVED` or `CORRECTED`). Attempting export returns HTTP 400.
  - **Immutable Audit Trail**: Every field decision and review submission appends an immutable audit event (`actor = REVIEWER`) to `record.audit_events` and `logs/audit.jsonl`.

---

## 📊 Benchmark Evaluation Metrics (12-Doc Corpus)
- **Baseline Verified Field Accuracy**: 84.92%
- **Agentic Verified Field Accuracy**: **100.0%**
- **Escalation Recall**: **100.0%** (100% of PII and corrupted fields correctly routed to human review/rescan)
- **Unnecessary Review Rate**: 13.33%
- **Agent Processing Duration**: **0.0189 sec / doc**

---

## 🛡️ Governance & Compliance Documents
- [docs/challenge-compliance.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/challenge-compliance.md) — Safety & Individual Entry Compliance Statement
- [docs/agent-use-disclosure.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/agent-use-disclosure.md) — Tool & Agent Disclosure Matrix
- [docs/submission-integrity.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/submission-integrity.md) — Work Categorization & Originality Certification
- [docs/qualification-gate-checklist.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/qualification-gate-checklist.md) — 11-Point Qualification Gate Checklist
- [docs/reproduction.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/reproduction.md) — Clean Environment Reproduction Guide
