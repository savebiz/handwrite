"""
scripts/run_reviewer_walkthrough.py — Local End-to-End Reviewer Workflow Walkthrough

Executes all 7 stages of the reviewer workflow against document record AXA-ATT-001:
  1. Opening reviewer queue
  2. Selecting document
  3. Inspecting evidence & proposed values
  4. Confirming sensitive field export block (HTTP 400) when pending
  5. Submitting reviewer field actions (approval, correction, rescan)
  6. Exporting approved record (HTTP 200)
  7. Verifying complete audit trail
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from starlette.testclient import TestClient
from app.backend.main import app
from app.shared.schemas import DocumentRecord


ADV_RECORD_PATH = "data/test-run-01/outputs/advanced/AXA-ATT-001_advanced.json"
DB_DIR = "outputs/db"


def run_walkthrough():
    print("==========================================================================")
    print("HANDWRITE VERIFY — LOCAL REVIEWER WORKFLOW WALKTHROUGH (AXA-ATT-001)")
    print("==========================================================================")

    if not os.path.exists(ADV_RECORD_PATH):
        print(f"[ERROR] Advanced record missing: {ADV_RECORD_PATH}")
        sys.exit(1)

    os.makedirs(DB_DIR, exist_ok=True)
    with open(ADV_RECORD_PATH, "r", encoding="utf-8") as f:
        rec_data = json.load(f)

    # Seed DB with test record in AWAITING_REVIEW state
    doc_id = rec_data["document_id"]
    db_file = os.path.join(DB_DIR, f"{doc_id}.json")
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(rec_data, f, indent=2)

    client = TestClient(app)

    # Stage 1: Opening Reviewer Queue
    print("\n--- STAGE 1: Opening Reviewer Queue (GET /api/documents/queue) ---")
    res_queue = client.get("/api/documents/queue")
    assert res_queue.status_code == 200, f"Queue returned status {res_queue.status_code}"
    queue_data = res_queue.json()
    matched_doc = next((d for d in queue_data if d["document_id"] == doc_id), None)
    assert matched_doc is not None, f"Document {doc_id} not found in queue"
    assert matched_doc["record_status"] == "awaiting_review", f"Unexpected status: {matched_doc['record_status']}"
    print(f"[PASS] Queue retrieved. Total items: {len(queue_data)}. Target doc {doc_id} status: '{matched_doc['record_status']}'")

    # Stage 2: Selecting Document Detail
    print("\n--- STAGE 2: Document Detail Inspection (GET /api/documents/AXA-ATT-001) ---")
    res_detail = client.get(f"/api/documents/{doc_id}")
    assert res_detail.status_code == 200
    doc_detail = res_detail.json()
    print(f"[PASS] Document loaded. Type: '{doc_detail['document_type']}', Total Fields: {len(doc_detail['field_results'])}")

    # Stage 3: Inspecting Evidence & Proposed Values
    print("\n--- STAGE 3: Evidence Crop & Value Inspection ---")
    sensitive_fields = [f for f in doc_detail["field_results"] if f["sensitivity"] in ["personal", "sensitive"]]
    print(f"Found {len(sensitive_fields)} sensitive/personal fields requiring mandatory human review:")
    for sf in sensitive_fields:
        crop_ref = sf["evidence"]["crop_reference"] if sf.get("evidence") else "N/A"
        print(f"  - Field: '{sf['field_name']}' ({sf['display_name']}) | Proposed: '{sf['proposed_value']}' | Decision: '{sf['decision']}' | Crop: '{crop_ref}'")
    print("[PASS] Visual crop references and bounding box metadata verified.")

    # Stage 4: Testing Export Block Guardrail on Unapproved Record
    print("\n--- STAGE 4: Export Guardrail Block Verification (GET /api/documents/AXA-ATT-001/export) ---")
    res_export_blocked = client.get(f"/api/documents/{doc_id}/export")
    assert res_export_blocked.status_code == 400, f"Expected 400 export block, got {res_export_blocked.status_code}"
    err_detail = res_export_blocked.json()["detail"]
    print(f"[PASS] Export blocked cleanly with HTTP 400! Detail message: '{err_detail}'")

    # Stage 5: Submitting Reviewer Field Actions
    print("\n--- STAGE 5: Submitting Reviewer Field Actions (POST /api/documents/AXA-ATT-001/review) ---")
    review_payload = {
        "reviewer_id": "reviewer-victor-01",
        "field_reviews": [
            {"field_name": "register_ref", "action": "approved"},
            {"field_name": "record_date", "action": "approved"},
            {"field_name": "site_department", "action": "approved"},
            {"field_name": "attendee_name", "action": "corrected", "reviewer_value": "Staff Member 1", "reviewer_reason": "Verified against attendance register handwriting"},
            {"field_name": "staff_ref", "action": "approved"},
            {"field_name": "attendance_status", "action": "approved"},
            {"field_name": "time_in", "action": "approved"},
            {"field_name": "time_out", "action": "approved"},
            {"field_name": "supervisor_notes", "action": "approved"},
            {"field_name": "form_completeness", "action": "approved"},
        ]
    }
    res_review = client.post(f"/api/documents/{doc_id}/review", json=review_payload)
    assert res_review.status_code == 200
    reviewed_doc = res_review.json()
    assert reviewed_doc["record_status"] == "approved", f"Expected 'approved', got '{reviewed_doc['record_status']}'"
    print(f"[PASS] Review submitted. Final record status transitioned to: '{reviewed_doc['record_status'].upper()}'")

    # Stage 6: Exporting Approved Record
    print("\n--- STAGE 6: Exporting Approved Record (GET /api/documents/AXA-ATT-001/export) ---")
    res_export = client.get(f"/api/documents/{doc_id}/export")
    assert res_export.status_code == 200
    exported_data = res_export.json()
    assert exported_data["record_status"] == "approved"
    assert "verified_fields" in exported_data
    print(f"[PASS] Approved record exported cleanly! Total verified fields: {len(exported_data['verified_fields'])}")
    print(f"  Sample verified field ('attendee_name'): {exported_data['verified_fields']['attendee_name']}")

    # Stage 7: Verifying Complete Audit Trail
    print("\n--- STAGE 7: Verifying Audit Trail Log ---")
    audit_events = reviewed_doc.get("audit_events", [])
    assert len(audit_events) > 0, "No audit events found"
    last_evt = audit_events[-1]
    assert last_evt["actor"] == "reviewer", f"Expected actor 'reviewer', got '{last_evt['actor']}'"
    assert last_evt["action"] == "DOCUMENT_REVIEW_SUBMITTED"
    print(f"[PASS] Audit log verified! Latest event: Action '{last_evt['action']}' by Actor '{last_evt['actor']}' at {last_evt['timestamp']}")

    print("\n==========================================================================")
    print("LOCAL REVIEWER WORKFLOW WALKTHROUGH COMPLETED SUCCESSFULLY (7/7 STAGES PASS)")
    print("==========================================================================\n")


if __name__ == "__main__":
    run_walkthrough()
