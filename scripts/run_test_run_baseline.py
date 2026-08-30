"""
scripts/run_test_run_baseline.py — Single-Pass Baseline Execution on test-run-01

Executes single-pass unverified baseline extraction across accepted files in test-run-01.
Outputs records to data/test-run-01/outputs/baseline/ and summary to summary.json.
"""

import sys
import os
import json
import time
import io

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from app.shared.pdf_utils import convert_pdf_to_image
from evaluation.baseline import run_baseline_extraction
from app.shared.schemas import DocumentRecord, RecordStatusEnum


MANIFEST_PATH = "data/test-run-01/manifest.json"
SOURCE_DIR = r"C:\Users\hp\OneDrive - Dataguard Document Management Limited\Projects\Project AXA\AXA Insurance\Test File\TrainData1"
OUTPUT_DIR = "data/test-run-01/outputs/baseline"
LOG_DIR = "data/test-run-01/logs"
LOG_FILE = os.path.join(LOG_DIR, "baseline.log")


class TeeLogger:
    def __init__(self, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.file = open(file_path, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)
        self.file.flush()

    def flush(self):
        self.stdout.flush()
        self.file.flush()


def run_baseline():
    logger = TeeLogger(LOG_FILE)
    sys.stdout = logger

    print("==========================================================================")
    print("HANDWRITE VERIFY — TEST-RUN-01 BASELINE EXTRACTION EXECUTION")
    print("==========================================================================")

    if not os.path.exists(MANIFEST_PATH):
        print(f"[ERROR] Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    files_list = [f for f in manifest.get("files", []) if f.get("status") == "accepted"]
    print(f"Loaded manifest {manifest['test_run_id']}. Accepted files: {len(files_list)} / {len(manifest.get('files', []))}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("data/test-run-01/renders", exist_ok=True)

    start_time = time.time()
    processed_count = 0
    failure_count = 0
    total_fields = 0
    correct_fields = 0
    records_written = []

    for idx, fentry in enumerate(files_list, 1):
        filename = fentry["filename"]
        pdf_path = os.path.join(SOURCE_DIR, filename)

        if not os.path.exists(pdf_path):
            print(f"[{idx}/{len(files_list)}] [FAIL] File not found: {pdf_path}")
            failure_count += 1
            continue

        doc_id = f"AXA-ATT-{idx:03d}"
        gold_path = os.path.join("data/test-run-01/gold-labels", f"{filename}.gold.json")

        if not os.path.exists(gold_path):
            print(f"[{idx}/{len(files_list)}] [FAIL] Gold label missing: {gold_path}")
            failure_count += 1
            continue

        # Render PDF page 1 to PNG
        safe_fname = filename.replace(" ", "_").replace(".pdf", "")
        rendered_png = os.path.join("data/test-run-01/renders", f"{safe_fname}.png")
        try:
            convert_pdf_to_image(pdf_path, rendered_png)
        except Exception as e:
            print(f"[{idx}/{len(files_list)}] [FAIL] PDF render error for {filename}: {e}")
            failure_count += 1
            continue

        sample_manifest_dict = {
            "document_id": doc_id,
            "document_type": fentry["document_type"],
            "difficulty": fentry.get("expected_difficulty", "medium"),
            "image_path": rendered_png,
            "gold_label_path": gold_path,
        }

        # Execute single-pass baseline extraction
        rec: DocumentRecord = run_baseline_extraction(sample_manifest_dict)

        # Enforce "Never claim approval" rule
        assert rec.record_status == RecordStatusEnum.AWAITING_REVIEW, "Baseline record claimed approval!"

        # Read gold label ground truth for scoring
        with open(gold_path, "r", encoding="utf-8") as gfile:
            gold_data = json.load(gfile)

        gold_fields_dict = {f["field_name"]: f.get("expected_value") for f in gold_data.get("fields", [])}

        for field in rec.field_results:
            total_fields += 1
            if field.proposed_value == gold_fields_dict.get(field.field_name):
                correct_fields += 1

        # Write output record JSON to data/test-run-01/outputs/baseline/
        out_record_path = os.path.join(OUTPUT_DIR, f"{doc_id}_baseline.json")
        with open(out_record_path, "w", encoding="utf-8") as outf:
            outf.write(rec.model_dump_json(indent=2))

        records_written.append(out_record_path)
        processed_count += 1

        print(f"[{idx}/{len(files_list)}] [SUCCESS] Processed {filename:<30} -> {doc_id}_baseline.json (Status: {rec.record_status.value})")

    duration = time.time() - start_time
    accuracy = (correct_fields / total_fields * 100) if total_fields > 0 else 0.0

    # Write summary.json
    summary_data = {
        "test_run_id": manifest["test_run_id"],
        "workflow": "baseline",
        "dataset_version": manifest.get("dataset_version", "2.0.0"),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files_processed": processed_count,
        "failures": failure_count,
        "total_fields_evaluated": total_fields,
        "correct_fields": correct_fields,
        "verified_field_accuracy_percent": round(accuracy, 2),
        "runtime_seconds": round(duration, 4),
        "avg_duration_per_file_seconds": round(duration / processed_count, 4) if processed_count > 0 else 0.0,
        "cost_usd": 0.0,
        "output_directory": OUTPUT_DIR,
        "log_file": LOG_FILE,
        "records_written": records_written,
        "limitations": [
            "No image quality pre-check (processes blurred/corrupted forms without rescan)",
            "No deterministic verification rules (skips pattern, date, and enum checks)",
            "No risk-aware triage (public/internal fields auto-accepted without rule checks)",
            "No visual evidence crop linkage (crop_reference = None)",
            "No human correction memory"
        ],
    }

    summary_path = os.path.join(OUTPUT_DIR, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as sf:
        json.dump(summary_data, sf, indent=2)

    print("\n==========================================================================")
    print("TEST-RUN-01 BASELINE SUMMARY REPORT")
    print("==========================================================================")
    print(f"Test Run ID:       {summary_data['test_run_id']}")
    print(f"Files Processed:   {summary_data['files_processed']} / {len(files_list)}")
    print(f"Failures:          {summary_data['failures']}")
    print(f"Total Fields:      {summary_data['total_fields_evaluated']}")
    print(f"Correct Fields:    {summary_data['correct_fields']}")
    print(f"Verified Accuracy: {summary_data['verified_field_accuracy_percent']}%")
    print(f"Runtime Seconds:   {summary_data['runtime_seconds']} sec")
    print(f"Output Summary:    {summary_path}")
    print(f"Log Captured To:   {LOG_FILE}")
    print("==========================================================================\n")

    sys.stdout = logger.stdout
    logger.file.close()


if __name__ == "__main__":
    run_baseline()
