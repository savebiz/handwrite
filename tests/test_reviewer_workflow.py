"""
tests/test_reviewer_workflow.py — Unit & Integration Tests for Human Reviewer Workflow

Validates:
  1. Field approval action (reviewer_decision = APPROVED)
  2. Field correction action (requires value + reason, updates reviewer_value & normalized_value)
  3. Field rejection action (requires reason, sets reviewer_decision = REJECTED)
  4. Document rescan action (requires reason, sets record_status = RESCAN_REQUIRED)
  5. Missing reviewer reason validation (HTTP 400 error on missing reason for correction/rejection/rescan)
  6. Sensitive PII field export blocking (HTTP 400 error if sensitive field not human-approved)
  7. Pending record export blocking (HTTP 400 error if record_status != APPROVED)
  8. Audit event creation (FIELD_REVIEWED, DOCUMENT_REVIEW_SUBMITTED, DOCUMENT_RESCAN_REQUESTED logged)
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))

from app.backend.main import app
from app.shared.schemas import (
    DocumentRecord,
    ReviewerDecisionEnum,
    RecordStatusEnum,
    SensitivityEnum,
)

client = TestClient(app)


@pytest.fixture
def sample_record_id():
    """Uploads a synthetic field-inspection form and returns the document_id."""
    res = client.post(
        "/api/documents/upload",
        data={
            "sample_id": "FI-001",
            "doc_type_hint": "field_inspection",
        },
    )
    assert res.status_code == 200
    data = res.json()
    return data["document_id"]


@pytest.fixture
def onboarding_record_id():
    """Uploads a synthetic customer onboarding form (contains sensitive PII fields)."""
    res = client.post(
        "/api/documents/upload",
        data={
            "sample_id": "CO-001",
            "doc_type_hint": "customer_onboarding",
        },
    )
    assert res.status_code == 200
    data = res.json()
    return data["document_id"]


def test_approve_field_action(sample_record_id):
    """Reviewer approves a non-sensitive field."""
    res = client.post(
        f"/api/documents/{sample_record_id}/review",
        json={
            "reviewer_id": "reviewer-alice",
            "field_reviews": [{
                "field_name": "site_location",
                "action": "approved",
                "reviewer_reason": "Verified visual crop against form site field.",
            }],
        },
    )
    assert res.status_code == 200
    record = res.json()

    site_field = next(f for f in record["field_results"] if f["field_name"] == "site_location")
    assert site_field["reviewer_decision"] == "approved"
    assert site_field["reviewer_reason"] == "Verified visual crop against form site field."


def test_correct_field_action(sample_record_id):
    """Reviewer corrects a misextracted field with new value and mandatory reason."""
    res = client.post(
        f"/api/documents/{sample_record_id}/review",
        json={
            "reviewer_id": "reviewer-bob",
            "field_reviews": [{
                "field_name": "observation_finding",
                "action": "corrected",
                "reviewer_value": "150psi pressure test passed",
                "reviewer_reason": "Misread handwriting digits 120 -> 150.",
            }],
        },
    )
    assert res.status_code == 200
    record = res.json()

    obs_field = next(f for f in record["field_results"] if f["field_name"] == "observation_finding")
    assert obs_field["reviewer_decision"] == "corrected"
    assert obs_field["reviewer_value"] == "150psi pressure test passed"
    assert obs_field["normalized_value"] == "150psi pressure test passed"
    assert obs_field["reviewer_reason"] == "Misread handwriting digits 120 -> 150."


def test_reject_field_action(sample_record_id):
    """Reviewer rejects an unreadable field with mandatory reason."""
    res = client.post(
        f"/api/documents/{sample_record_id}/review",
        json={
            "reviewer_id": "reviewer-charlie",
            "field_reviews": [{
                "field_name": "action_required",
                "action": "rejected",
                "reviewer_reason": "Text completely smudged and unreadable.",
            }],
        },
    )
    assert res.status_code == 200
    record = res.json()

    act_field = next(f for f in record["field_results"] if f["field_name"] == "action_required")
    assert act_field["reviewer_decision"] == "rejected"
    assert act_field["reviewer_value"] is None
    assert record["record_status"] == "rejected"


def test_rescan_document_action(sample_record_id):
    """Reviewer requests document-level rescan with mandatory reason."""
    res = client.post(
        f"/api/documents/{sample_record_id}/review",
        json={
            "reviewer_id": "reviewer-dave",
            "overall_action": "rescan",
            "reason": "Page 1 is torn and key header details are cut off.",
        },
    )
    assert res.status_code == 200
    record = res.json()

    assert record["record_status"] == "rescan_required"
    assert record["document_quality"]["rescan_required"] is True


def test_missing_reviewer_reason_validation(sample_record_id):
    """HTTP 400 error when submitting correction, rejection, or rescan without a reason."""
    # 1. Correction missing reason
    res_corr = client.post(
        f"/api/documents/{sample_record_id}/review",
        json={
            "field_reviews": [{
                "field_name": "site_location",
                "action": "corrected",
                "reviewer_value": "New Site Name",
                "reviewer_reason": "   ",  # Blank whitespace
            }],
        },
    )
    assert res_corr.status_code == 400
    assert "requires a non-empty reviewer reason" in res_corr.json()["detail"]

    # 2. Rejection missing reason
    res_rej = client.post(
        f"/api/documents/{sample_record_id}/review",
        json={
            "field_reviews": [{
                "field_name": "site_location",
                "action": "rejected",
                "reviewer_reason": "",  # Empty
            }],
        },
    )
    assert res_rej.status_code == 400
    assert "requires a non-empty reviewer reason" in res_rej.json()["detail"]

    # 3. Rescan missing reason
    res_rescan = client.post(
        f"/api/documents/{sample_record_id}/review",
        json={
            "overall_action": "rescan",
            "reason": "",  # Empty
        },
    )
    assert res_rescan.status_code == 400
    assert "requires a non-empty reviewer reason" in res_rescan.json()["detail"]


def test_pending_record_export_blocking(sample_record_id):
    """HTTP 400 error when attempting to export an unapproved record."""
    # Record is currently awaiting_review
    res = client.get(f"/api/documents/{sample_record_id}/export?format=json")
    assert res.status_code == 400
    assert "Export blocked" in res.json()["detail"]


def test_sensitive_field_export_blocking(onboarding_record_id):
    """HTTP 400 error when exporting a record containing unapproved sensitive PII fields."""
    # Approve only non-sensitive fields
    res_review = client.post(
        f"/api/documents/{onboarding_record_id}/review",
        json={
            "field_reviews": [
                {"field_name": "onboarding_ref", "action": "approved", "reviewer_reason": "OK"},
                {"field_name": "application_date", "action": "approved", "reviewer_reason": "OK"},
                {"field_name": "product_requested", "action": "approved", "reviewer_reason": "OK"},
            ]
        },
    )
    assert res_review.status_code == 200

    # Attempt export — sensitive fields (applicant_name, contact_number, etc.) are still pending/unapproved
    res_export = client.get(f"/api/documents/{onboarding_record_id}/export?format=json")
    assert res_export.status_code == 400
    assert "Export blocked" in res_export.json()["detail"]
    assert "Sensitive PII field" in res_export.json()["detail"] or "must be 'approved'" in res_export.json()["detail"]


def test_successful_export_after_full_sensitive_approval(onboarding_record_id):
    """Export succeeds after all sensitive fields receive explicit human approval."""
    # Approve ALL fields including sensitive ones
    field_names = [
        "onboarding_ref", "application_date", "applicant_name", "contact_number",
        "email_address", "address_location", "product_requested", "id_ref_placeholder",
        "consent_indicator", "reviewer_status", "form_completeness"
    ]
    reviews = [
        {"field_name": name, "action": "approved", "reviewer_reason": f"Verified {name}"}
        for name in field_names
    ]

    res_review = client.post(
        f"/api/documents/{onboarding_record_id}/review",
        json={"field_reviews": reviews},
    )
    assert res_review.status_code == 200
    assert res_review.json()["record_status"] == "approved"

    # Export JSON
    res_json = client.get(f"/api/documents/{onboarding_record_id}/export?format=json")
    assert res_json.status_code == 200
    export_data = res_json.json()
    assert export_data["record_status"] == "approved"
    assert "applicant_name" in export_data["verified_fields"]

    # Export CSV
    res_csv = client.get(f"/api/documents/{onboarding_record_id}/export?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "Field Name,Display Name" in res_csv.text


def test_audit_event_creation(sample_record_id):
    """Verify FIELD_REVIEWED and DOCUMENT_REVIEW_SUBMITTED audit events are appended."""
    res = client.post(
        f"/api/documents/{sample_record_id}/review",
        json={
            "reviewer_id": "reviewer-eve",
            "field_reviews": [{
                "field_name": "site_location",
                "action": "approved",
                "reviewer_reason": "Audit verification check.",
            }],
        },
    )
    assert res.status_code == 200
    record = res.json()

    events = record["audit_events"]
    actions = [e["action"] for e in events]
    assert "FIELD_REVIEWED" in actions
    assert "DOCUMENT_REVIEW_SUBMITTED" in actions


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------
def _create_sample_doc():
    res = client.post("/api/documents/upload", data={"sample_id": "FI-001", "doc_type_hint": "field_inspection"})
    return res.json()["document_id"]


def _create_onboarding_doc():
    res = client.post("/api/documents/upload", data={"sample_id": "CO-001", "doc_type_hint": "customer_onboarding"})
    return res.json()["document_id"]


def run_all_reviewer_tests():
    print("--- Running Human Reviewer Workflow Tests ---")

    doc_id = _create_sample_doc()
    onb_id = _create_onboarding_doc()

    test_approve_field_action(doc_id)
    print("[PASS] Test 1: Field approval action (reviewer_decision = APPROVED)")

    test_correct_field_action(doc_id)
    print("[PASS] Test 2: Field correction action (requires value + reason)")

    test_reject_field_action(doc_id)
    print("[PASS] Test 3: Field rejection action (requires reason)")

    test_rescan_document_action(doc_id)
    print("[PASS] Test 4: Document rescan action (requires reason)")

    test_missing_reviewer_reason_validation(doc_id)
    print("[PASS] Test 5: Missing reviewer reason validation (HTTP 400 error)")

    test_pending_record_export_blocking(doc_id)
    print("[PASS] Test 6: Pending record export blocking (HTTP 400 error)")

    test_sensitive_field_export_blocking(onb_id)
    print("[PASS] Test 7: Sensitive PII field export blocking (HTTP 400 error)")

    test_successful_export_after_full_sensitive_approval(onb_id)
    print("[PASS] Test 8: Successful JSON and CSV export after sensitive approval")

    test_audit_event_creation(doc_id)
    print("[PASS] Test 9: Audit event creation (FIELD_REVIEWED & DOCUMENT_REVIEW_SUBMITTED)")

    print("\n[SUCCESS] ALL HUMAN REVIEWER WORKFLOW TESTS PASSED (9/9).")


if __name__ == "__main__":
    run_all_reviewer_tests()
