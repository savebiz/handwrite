import os
import sys

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.backend.main import app
from app.shared.schemas import RecordStatusEnum

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_upload_sample_document():
    res = client.post("/api/documents/upload", data={"sample_id": "FI-001"})
    assert res.status_code == 200
    data = res.json()
    assert data["document_id"] == "FI-001"
    assert data["document_type"] == "field_inspection"


def test_review_and_export_flow():
    # Process document
    client.post("/api/documents/upload", data={"sample_id": "CO-001"})

    # Fetch document detail
    doc_res = client.get("/api/documents/CO-001")
    assert doc_res.status_code == 200
    doc_data = doc_res.json()

    # Attempt export BEFORE human review -> Should fail with 400
    export_fail = client.get("/api/documents/CO-001/export")
    assert export_fail.status_code == 400

    # Submit reviewer decisions
    reviews = []
    for field in doc_data["field_results"]:
        reviews.append({
            "field_name": field["field_name"],
            "action": "approved",
            "reviewer_value": field["normalized_value"] or field["proposed_value"],
            "reviewer_reason": "Verified by test operator"
        })

    review_res = client.post("/api/documents/CO-001/review", json={
        "reviewer_id": "op-test",
        "field_reviews": reviews
    })
    assert review_res.status_code == 200
    reviewed_doc = review_res.json()
    assert reviewed_doc["record_status"] == RecordStatusEnum.APPROVED.value

    # Export JSON after approval -> Should succeed with 200
    export_success = client.get("/api/documents/CO-001/export?format=json")
    assert export_success.status_code == 200
    export_data = export_success.json()
    assert "verified_fields" in export_data


def run_all_api_tests():
    print("--- Running FastAPI & Reviewer Workflow Tests ---")
    test_api_health()
    print("[PASS] API Health Check Test")
    test_upload_sample_document()
    print("[PASS] Document Upload & Pipeline Trigger Test")
    test_review_and_export_flow()
    print("[PASS] End-to-End Human Review & Export Guardrail Test")
    print("\n[SUCCESS] ALL API & REVIEWER WORKFLOW TESTS PASSED CLEANLY (3/3).")


if __name__ == "__main__":
    run_all_api_tests()
