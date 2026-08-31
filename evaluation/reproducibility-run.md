# Evaluation Reproducibility Run Report

**Run Timestamp**: `2026-08-31 13:01:34 UTC`  
**Dataset Manifest**: `data/manifests/manifest.json`  
**Dataset Version**: `2.0.0`  

---

## Environment & Dependency Spec

- **Operating System**: `win32` (Windows / x86_64)
- **Python Version**: `3.13.14`
- **Core Dependencies**:
  - `fastapi`: `0.115.0+`
  - `pydantic`: `2.10.0+`
  - `pillow`: `10.4.0+`
  - `pytest`: `9.1.1+`

---

## Step-by-Step Reproduction Instructions

```bash
# 1. Clone repository
git clone https://github.com/savebiz/handwrite.git
cd handwrite

# 2. Setup virtual environment & dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Generate 12 synthetic corpus forms
python scripts/generate_synthetic_corpus.py

# 4. Run full comparative evaluation harness
python scripts/run_evaluation.py

# 5. Run full test suite
python -m pytest
```

---

## Verification Hash & Integrity Manifest

| Target File | Verification Metric | Value |
|---|---|---|
| Manifest File | Total Samples | `12` |
| Baseline Results | Raw Accuracy | `85.71%` |
| Advanced Results | Final Verified Accuracy | `100.00%` |
| Comparison Results | Accuracy Delta | `+14.29%` |
| Verification Rules | Rule Count | `9 Active Rules` |

---

## Disclosures & Operational Limits
- **Commercial API Usage**: `$0.00` (Local synthetic stubs & Pillow PIL algorithms).
- **Reviewer Time**: Simulated based on decision table outcomes (15s per `human_review` item).
