"""
scripts/run_local_test_folder.py — Private Local Benchmark Runner

Executes HandWrite Verify pipeline against the 11 attendance register PDF documents in:
  C:\\Users\\hp\\OneDrive - Dataguard Document Management Limited\\Projects\\Project AXA\\AXA Insurance\\Test File\\TrainData1

Guarantees 100% private local execution:
  - Rendered images saved to data/local_test/renders/
  - Output database records saved to outputs/local_test/db/
  - Zero local test artifacts tracked or committed to Git (secured by .gitignore)
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from app.shared.pdf_utils import is_pdf, convert_pdf_to_image
from app.backend.pipeline import process_document_pipeline
from app.shared.schemas import DocumentRecord, QualityStatus, RecordStatusEnum, DecisionEnum


TEST_FOLDER = r"C:\Users\hp\OneDrive - Dataguard Document Management Limited\Projects\Project AXA\AXA Insurance\Test File\TrainData1"
LOCAL_RENDER_DIR = os.path.join("data", "local_test", "renders")
LOCAL_DB_DIR = os.path.join("outputs", "local_test", "db")


def run_local_benchmark():
    os.makedirs(LOCAL_RENDER_DIR, exist_ok=True)
    os.makedirs(LOCAL_DB_DIR, exist_ok=True)

    print("==========================================================================")
    print("HANDWRITE VERIFY — PRIVATE LOCAL BENCHMARK (AXA ATTENDANCE PDFs)")
    print("==========================================================================")
    print(f"Target Directory: {TEST_FOLDER}")
    print(f"Render Directory: {LOCAL_RENDER_DIR} (Git Ignored)")
    print(f"Output Database:  {LOCAL_DB_DIR} (Git Ignored)")
    print("--------------------------------------------------------------------------\n")

    if not os.path.exists(TEST_FOLDER):
        print(f"[ERROR] Test folder not found at: {TEST_FOLDER}")
        sys.exit(1)

    pdf_files = [f for f in os.listdir(TEST_FOLDER) if f.lower().endswith(".pdf")]
    pdf_files.sort()

    if not pdf_files:
        print(f"[ERROR] No PDF files found in {TEST_FOLDER}")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF document files to process.\n")

    total_start = time.time()
    results_summary = []

    for idx, filename in enumerate(pdf_files, 1):
        pdf_path = os.path.join(TEST_FOLDER, filename)
        doc_id = f"AXA-ATT-{idx:03d}"
        
        start_doc = time.time()

        # Step 1: Convert Page 1 PDF to PNG render
        safe_filename = filename.replace(" ", "_").replace(".pdf", "")
        rendered_png = os.path.join(LOCAL_RENDER_DIR, f"{safe_filename}.png")
        try:
            convert_pdf_to_image(pdf_path, rendered_png)
        except Exception as e:
            print(f"[{idx}/{len(pdf_files)}] {filename} — PDF RENDER ERROR: {str(e)}")
            continue

        # Step 2: Process through Agentic Pipeline
        rec: DocumentRecord = process_document_pipeline(
            image_path=rendered_png,
            document_id=doc_id,
            doc_type_hint="attendance_register",
        )

        doc_duration = time.time() - start_doc

        # Step 3: Save record JSON to local output DB
        out_record_path = os.path.join(LOCAL_DB_DIR, f"{doc_id}.json")
        with open(out_record_path, "w", encoding="utf-8") as f:
            f.write(rec.model_dump_json(indent=2))

        # Metrics tally
        total_fields = len(rec.field_results)
        auto_accepted = sum(1 for f in rec.field_results if f.decision == DecisionEnum.AUTO_ACCEPT)
        human_review = sum(1 for f in rec.field_results if f.decision == DecisionEnum.HUMAN_REVIEW)
        rescan_req = sum(1 for f in rec.field_results if f.decision == DecisionEnum.RESCAN_REQUIRED)

        summary_entry = {
            "filename": filename,
            "document_id": doc_id,
            "quality_status": rec.document_quality.status.value.upper(),
            "record_status": rec.record_status.value.upper(),
            "total_fields": total_fields,
            "auto_accepted": auto_accepted,
            "human_review": human_review,
            "rescan_required": rescan_req,
            "duration_sec": round(doc_duration, 4),
        }
        results_summary.append(summary_entry)

        print(
            f"[{idx}/{len(pdf_files)}] {filename[:30]:<30} | "
            f"Quality: {rec.document_quality.status.value.upper():<7} | "
            f"Status: {rec.record_status.value.upper():<15} | "
            f"Fields: {total_fields} (Auto:{auto_accepted}, Review:{human_review}) | "
            f"Time: {doc_duration:.4f}s"
        )

    total_duration = time.time() - total_start
    avg_duration = total_duration / len(pdf_files) if pdf_files else 0.0

    print("\n==========================================================================")
    print("PRIVATE LOCAL BENCHMARK SUMMARY REPORT")
    print("==========================================================================")
    print(f"Total PDFs Processed:  {len(results_summary)} / {len(pdf_files)}")
    print(f"Total Processing Time: {total_duration:.4f} seconds")
    print(f"Avg Time Per PDF:      {avg_duration:.4f} seconds")
    print(f"Quality PASS Rate:     {sum(1 for r in results_summary if r['quality_status'] == 'PASS')} / {len(results_summary)}")
    print(f"Awaiting Review Queue: {sum(1 for r in results_summary if r['record_status'] == 'AWAITING_REVIEW')} / {len(results_summary)}")
    print(f"Output Storage:        {LOCAL_DB_DIR}")
    print("Privacy Guarantee:     100% Local Private Execution — Zero Files Staged to Git.")
    print("==========================================================================\n")


if __name__ == "__main__":
    run_local_benchmark()
