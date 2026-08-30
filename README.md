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

# 4. Run Baseline Scoring & Unit Test Suite
python scripts/run_baseline_scoring.py   # Runs single-pass baseline, saves outputs/baseline_results.json
python scripts/run_baseline_tests.py     # Standalone baseline unit tests (5/5 PASS)
python scripts/run_corpus_tests.py       # Corpus validation tests (19/19 PASS)
python scripts/run_schema_tests.py       # Schema validation tests (14/14 PASS)
python tests/test_pipeline.py            # Agent pipeline tests (4/4 PASS)
python tests/test_api.py                 # FastAPI & Reviewer workflow tests (3/3 PASS)

# 5. Run FastAPI Backend API
uvicorn app.backend.main:app --reload --port 8000
```

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
