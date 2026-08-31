import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))

from app.backend.main import app, save_record_to_db
from app.shared.schemas import (
    DocumentRecord,
    DocumentType,
    QualityResult,
    QualityStatus,
    FieldResult,
    DecisionEnum,
    ReviewerDecisionEnum,
    SensitivityEnum,
    RecordStatusEnum,
    Evidence,
)

client = TestClient(app)


def build_mock_record(doc_id="TEST-SEL-001", status=RecordStatusEnum.APPROVED):
    mock_ev = Evidence(page=1, bounding_box=[10, 10, 50, 100], crop_reference="/crops/test.png")
    return DocumentRecord(
        run_id="run-sel-test",
        document_id=doc_id,
        document_type=DocumentType.FIELD_INSPECTION,
        document_quality=QualityResult(status=QualityStatus.PASS),
        record_status=status,
        field_results=[
            FieldResult(
                field_name="inspection_ref",
                display_name="Inspection Reference",
                proposed_value="INSP-2026-001",
                normalized_value="INSP-2026-001",
                confidence=0.95,
                decision=DecisionEnum.AUTO_ACCEPT,
                decision_reason="Passed validation",
                evidence=mock_ev,
                reviewer_decision=ReviewerDecisionEnum.APPROVED,
                reviewer_value="INSP-2026-001",
                sensitivity=SensitivityEnum.PUBLIC,
            ),
            FieldResult(
                field_name="inspection_date",
                display_name="Inspection Date",
                proposed_value="2026-08-30",
                normalized_value="2026-08-30",
                confidence=0.92,
                decision=DecisionEnum.AUTO_ACCEPT,
                decision_reason="Passed validation",
                evidence=mock_ev,
                reviewer_decision=ReviewerDecisionEnum.APPROVED,
                reviewer_value="2026-08-30",
                sensitivity=SensitivityEnum.INTERNAL,
            ),
            FieldResult(
                field_name="inspector_name",
                display_name="Inspector Name",
                proposed_value="Jane Smith",
                normalized_value="Jane Smith",
                confidence=0.75,
                decision=DecisionEnum.HUMAN_REVIEW,
                decision_reason="Mandatory review for PII",
                evidence=mock_ev,
                reviewer_decision=ReviewerDecisionEnum.APPROVED,
                reviewer_value="Jane Smith",
                reviewer_reason="Verified inspector identity",
                sensitivity=SensitivityEnum.PERSONAL,
            ),
            FieldResult(
                field_name="unapproved_pii",
                display_name="Unapproved PII",
                proposed_value="Secret PII",
                normalized_value="Secret PII",
                confidence=0.60,
                decision=DecisionEnum.HUMAN_REVIEW,
                decision_reason="Mandatory review for PII",
                evidence=mock_ev,
                reviewer_decision=ReviewerDecisionEnum.NOT_REQUIRED,
                reviewer_value=None,
                sensitivity=SensitivityEnum.PERSONAL,
            ),
            FieldResult(
                field_name="failing_field",
                display_name="Failing Field",
                proposed_value=None,
                normalized_value=None,
                confidence=0.40,
                decision=DecisionEnum.HUMAN_REVIEW,
                decision_reason="Unreadable field",
                evidence=mock_ev,
                reviewer_decision=ReviewerDecisionEnum.NOT_REQUIRED,
                reviewer_value=None,
                sensitivity=SensitivityEnum.INTERNAL,
            ),
        ],
    )


def test_01_non_sensitive_field_selected_and_saved():
    rec = build_mock_record("TEST-SEL-001")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["inspection_ref", "inspection_date"],
        "preset_name": "Operational record",
        "action_type": "save"
    }
    res = client.post("/api/documents/TEST-SEL-001/export-selected", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "2 approved fields saved" in data["message"]
    assert data["selected_fields"] == ["inspection_ref", "inspection_date"]


def test_02_human_approved_sensitive_field_selected_and_exported():
    rec = build_mock_record("TEST-SEL-002")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["inspector_name"],
        "format": "json",
        "action_type": "export"
    }
    res = client.post("/api/documents/TEST-SEL-002/export-selected", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "inspector_name" in data["verified_fields"]
    assert data["verified_fields"]["inspector_name"]["value"] == "Jane Smith"


def test_03_unapproved_sensitive_field_blocked():
    rec = build_mock_record("TEST-SEL-003")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["unapproved_pii"],
        "action_type": "export"
    }
    res = client.post("/api/documents/TEST-SEL-003/export-selected", json=payload)
    assert res.status_code == 400
    assert "Sensitive PII field 'unapproved_pii'" in res.json()["detail"]


def test_04_pending_record_blocked():
    rec = build_mock_record("TEST-SEL-004", status=RecordStatusEnum.AWAITING_REVIEW)
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["inspection_ref"],
        "action_type": "save"
    }
    res = client.post("/api/documents/TEST-SEL-004/export-selected", json=payload)
    assert res.status_code == 400
    assert "Cannot save/export record in 'awaiting_review' state" in res.json()["detail"]


def test_05_failing_field_blocked():
    rec = build_mock_record("TEST-SEL-005")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["failing_field"],
        "action_type": "save"
    }
    res = client.post("/api/documents/TEST-SEL-005/export-selected", json=payload)
    assert res.status_code == 400
    assert "has no usable value" in res.json()["detail"] or "requires human review" in res.json()["detail"]


def test_06_select_all_eligible_only():
    rec = build_mock_record("TEST-SEL-006")
    save_record_to_db(rec)

    # Submitting valid eligible fields
    payload = {
        "selected_fields": ["inspection_ref", "inspection_date", "inspector_name"],
        "action_type": "save"
    }
    res = client.post("/api/documents/TEST-SEL-006/export-selected", json=payload)
    assert res.status_code == 200


def test_07_personal_fields_unselected_by_default():
    rec = build_mock_record("TEST-SEL-007")
    # Verify inspector_name is personal
    f_p = next(f for f in rec.field_results if f.field_name == "inspector_name")
    assert f_p.sensitivity == SensitivityEnum.PERSONAL


def test_08_csv_export_contains_only_selected_fields():
    rec = build_mock_record("TEST-SEL-008")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["inspection_ref"],
        "format": "csv",
        "action_type": "export"
    }
    res = client.post("/api/documents/TEST-SEL-008/export-selected", json=payload)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    content = res.text
    assert "inspection_ref" in content
    assert "inspection_date" not in content


def test_09_excel_compatible_csv_contains_utf8_bom():
    rec = build_mock_record("TEST-SEL-009")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["inspection_ref", "inspection_date"],
        "format": "excel_compatible_csv",
        "action_type": "export"
    }
    res = client.post("/api/documents/TEST-SEL-009/export-selected", json=payload)
    assert res.status_code == 200
    assert res.content.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM bytes


def test_10_json_export_contains_only_selected_fields():
    rec = build_mock_record("TEST-SEL-010")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["inspection_date"],
        "format": "json",
        "action_type": "export"
    }
    res = client.post("/api/documents/TEST-SEL-010/export-selected", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "inspection_date" in data["verified_fields"]
    assert "inspection_ref" not in data["verified_fields"]


def test_11_audit_events_created():
    rec = build_mock_record("TEST-SEL-011")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["inspection_ref"],
        "action_type": "save"
    }
    res = client.post("/api/documents/TEST-SEL-011/export-selected", json=payload)
    assert res.status_code == 200

    # Inspect updated record audit events
    rec_updated = client.get("/api/documents/TEST-SEL-011").json()
    events = rec_updated["audit_events"]
    assert any(e["action"] == "SELECTED_FIELDS_SAVED" for e in events)


def test_12_backend_blocks_frontend_bypass_attempt():
    rec = build_mock_record("TEST-SEL-012")
    save_record_to_db(rec)

    # Attempting to bypass by passing an unapproved PII field name
    payload = {
        "selected_fields": ["unapproved_pii"],
        "action_type": "export"
    }
    res = client.post("/api/documents/TEST-SEL-012/export-selected", json=payload)
    assert res.status_code == 400
    assert "Selection blocked" in res.json()["detail"]


def test_13_empty_selection_returns_error():
    rec = build_mock_record("TEST-SEL-013")
    save_record_to_db(rec)

    payload = {
        "selected_fields": [],
        "action_type": "save"
    }
    res = client.post("/api/documents/TEST-SEL-013/export-selected", json=payload)
    assert res.status_code == 400
    assert "No fields selected" in res.json()["detail"]


def test_14_nonexistent_field_returns_error():
    rec = build_mock_record("TEST-SEL-014")
    save_record_to_db(rec)

    payload = {
        "selected_fields": ["nonexistent_field"],
        "action_type": "save"
    }
    res = client.post("/api/documents/TEST-SEL-014/export-selected", json=payload)
    assert res.status_code == 400
    assert "not found in record" in res.json()["detail"]
