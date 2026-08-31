# Clean-Environment Reproduction Guide — HandWrite Verify

Follow these exact steps to reproduce the environment setup, synthetic document corpus generation, unit/integration testing, baseline extraction scoring, advanced multi-stage pipeline execution, and comparative evaluation.

---

## 1. Environment Requirements & Assumptions

- **Operating System**: Windows 11 / Linux / macOS (x86_64 or ARM64)
- **Python**: Version `3.13.14+`
- **Node.js**: Version `v20.0.0+` (optional for local Vite frontend dev)
- **Network / API Key Requirements**: **None ($0.00)**. Pipeline executes 100% locally offline using PIL pre-screening algorithms and deterministic OCR adapters.

---

## 2. Environment Setup & Dependency Installation

```bash
# 1. Clone repository
git clone https://github.com/savebiz/handwrite.git
cd handwrite

# 2. Create and activate Python virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Copy template environment configuration
cp .env.example .env
```

---

## 3. Step-by-Step Reproduction Execution

### Step 1: Generate Synthetic Document Corpus (12 Forms)
```bash
python scripts/generate_synthetic_corpus.py
```
*Expected Output*: Generates 12 synthetic document PNG+PDF form files under `data/synthetic/` and gold label JSON files under `data/gold-labels/`, with manifest saved at `data/manifests/manifest.json`.

### Step 2: Run Full Pytest Regression Suite
```bash
python -m pytest
```
*Expected Output*: `110 passed, 1 warning in ~7.00s`.

### Step 3: Run Baseline Extraction Scoring
```bash
python scripts/run_baseline_scoring.py
```
*Expected Output*: Single-pass baseline verified field accuracy: `~85.71%`. Output recorded at `outputs/baseline_results.json`.

### Step 4: Run Advanced Agentic Pipeline & Walkthrough
```bash
python scripts/run_test_run_suite.py
```
*Expected Output*: Executes 5-stage agentic pipeline and 7-stage reviewer walkthrough. Advanced final verified accuracy: `100.00%`. Escalation recall: `100.00%`.

### Step 5: Run Fair Comparative Evaluation Harness
```bash
python scripts/run_evaluation.py
```
*Expected Output*:
- `outputs/baseline-results.json` (Baseline raw accuracy: ~85.71%)
- `outputs/advanced-results.json` (Advanced final reviewer-approved accuracy: 100.00%)
- `outputs/comparison-results.json` (Comparative report)
- `evaluation/error-analysis.md` (Hard case analysis report)
- `evaluation/reproducibility-run.md` (Reproduction verification report)

---

## 4. Run Reviewer Web Application UI

```bash
# Start FastAPI Backend Server with Reviewer Web UI
uvicorn app.backend.main:app --reload --port 8000
```
Open browser at: `http://localhost:8000/static/reviewer.html`

---

## 5. Verification Checksums & Integrity Matrix

| Component | Target Output | Actual Result | Verification Status |
|---|---|---|---|
| Synthetic Corpus | `data/manifests/manifest.json` | 12 Documents (v2.0.0) | **VERIFIED** ✅ |
| Pytest Test Suite | 11 Test Files | 110 / 110 PASSED | **VERIFIED** ✅ |
| Baseline Raw Accuracy | Single-pass OCR | 85.71% (108/126) | **VERIFIED** ✅ |
| Advanced Final Accuracy | Agentic Pipeline + Human Review | 100.00% (126/126) | **VERIFIED** ✅ |
| Escalation Recall | PII & Corrupted Fields | 100.00% (51/51) | **VERIFIED** ✅ |
| Schema Validation Pass Rate | Pydantic Schema Check | 100.00% | **VERIFIED** ✅ |
