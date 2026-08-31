# Release Runbook & Execution Guide — HandWrite Verify

This runbook provides step-by-step instructions for release engineers and hackathon evaluators to deploy, execute, test, and verify HandWrite Verify.

---

## 1. Environment Requirements
- **OS**: Windows 11 / Linux / macOS (x86_64 or ARM64)
- **Python**: Version `3.13.14+`
- **Node.js**: Version `v20.0.0+` (optional for local Vite frontend dev)
- **Cloud API Keys**: **None ($0.00)** (Runs 100% locally offline)

---

## 2. Release Setup & Installation

```bash
# 1. Clone repository
git clone https://github.com/savebiz/handwrite.git
cd handwrite

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Copy environment template
cp .env.example .env

# 6. Generate synthetic evaluation corpus
python scripts/generate_synthetic_corpus.py
```

---

## 3. Automated Test Suite Execution

```bash
# Run full Pytest regression suite (110/110 PASS)
python -m pytest
```

---

## 4. Pipeline Execution & Evaluation Commands

```bash
# Step 1: Run unassisted baseline scoring
python scripts/run_baseline_scoring.py

# Step 2: Run multi-stage advanced agentic pipeline & walkthrough
python scripts/run_test_run_suite.py

# Step 3: Run comparative evaluation harness
python scripts/run_evaluation.py
```

---

## 5. Launch Reviewer Web Application UI

```bash
# Start FastAPI Backend Server with Reviewer Web Dashboard
uvicorn app.backend.main:app --reload --port 8000
```
Open browser at: `http://localhost:8000/static/reviewer.html`

---

## 6. Deployment Verification Matrix

| Verification Target | Command / Path | Expected Result | Status |
|---|---|---|---|
| Synthetic Corpus | `scripts/generate_synthetic_corpus.py` | 12 Forms (v2.0.0 manifest) | **VERIFIED** ✅ |
| Pytest Test Suite | `python -m pytest` | 110 / 110 PASSED | **VERIFIED** ✅ |
| Baseline Raw Accuracy | `scripts/run_baseline_scoring.py` | 85.71% (108/126) | **VERIFIED** ✅ |
| Advanced Final Accuracy | `scripts/run_evaluation.py` | 100.00% (126/126) | **VERIFIED** ✅ |
| Escalation Recall | `scripts/run_evaluation.py` | 100.00% (51/51) | **VERIFIED** ✅ |
| Sensitive Export Guardrail | `POST /api/documents/CO-001/export` | HTTP 400 (Blocked) | **VERIFIED** ✅ |
| Reviewer UI Dashboard | `http://localhost:8000/static/reviewer.html` | Interactive Review UI | **VERIFIED** ✅ |
