# Test-Run 01 — Execution & Verification Guide

## Purpose
This directory (`data/test-run-01/`) defines a isolated, structured test environment for evaluating HandWrite Verify against external sample files (e.g. from local test folder `C:\Users\hp\OneDrive - Dataguard Document Management Limited\Projects\Project AXA\AXA Insurance\Test File\TrainData1` or `data/test-run-01/raw_files/`).

---

## 🛡️ Mandatory Safety Rules
> [!CAUTION]
> 1. **Synthetic / Public Data Only**: All test files MUST be 100% synthetic, public sample forms, or approved anonymized test data.
> 2. **Zero Real Customer Data / Real PII**: No real customer names, policy numbers, tax IDs, addresses, or phone numbers may be placed here or committed.
> 3. **No Secrets / Production Systems**: Do not include secrets, API keys, or production database credentials.

---

## 📥 How to Add Test Files

1. Copy your synthetic/public test form files (`.png`, `.jpg`, `.pdf`) into:
   ```text
   data/test-run-01/raw_files/
   ```
   *Or reference them directly from external local folder `C:\Users\hp\OneDrive - Dataguard Document Management Limited\Projects\Project AXA\AXA Insurance\Test File\TrainData1`.*

2. Update `data/test-run-01/manifest.json` to list each filename, document_type (`field_inspection` or `customer_onboarding`), and expected difficulty.

3. Add corresponding ground truth gold label files in `data/test-run-01/gold-labels/<filename>.gold.json` using the templates provided.

---

## 🚀 How to Run Workflows & Evaluation

### 1. Single-Pass Baseline Scoring
```bash
python scripts/run_baseline_scoring.py data/test-run-01/manifest.json outputs/test-run-01/baseline_results.json
```

### 2. Advanced Agentic Pipeline Execution
```bash
python -c "
import json
from app.backend.pipeline import process_document_pipeline

with open('data/test-run-01/manifest.json', 'r') as f:
    manifest = json.load(f)

for sample in manifest['samples']:
    record = process_document_pipeline(
        image_path=sample['image_path'],
        doc_type_hint=sample['document_type']
    )
    print(f'Processed {sample[\"filename\"]}: {record.record_status.value}')
"
```

### 3. Full Comparative Evaluation Benchmark
```bash
python -c "
from evaluation.evaluate import evaluate_corpus
evaluate_corpus('data/test-run-01/manifest.json')
"
```

---

## 📁 Where Outputs Will Appear
- **Machine-Readable Baseline Output**: `outputs/test-run-01/baseline_results.json`
- **Processed Record Outputs**: `outputs/db/<doc_id>.json`
- **Evidence Bounding-Box Crops**: `outputs/crops/<doc_id>_<field_name>.png`
- **Evaluation Benchmark Summary**: `outputs/evaluation_results.json`
- **Audit Logs**: `logs/audit.jsonl`
