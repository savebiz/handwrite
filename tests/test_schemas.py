import pytest
from pydantic import ValidationError
from app.shared.schemas import (
    DocumentRecord,
    DocumentType,
    QualityResult,
    QualityStatus,
    FieldResult,
    DecisionEnum,
    SensitivityEnum,
    Evidence,
    VerificationCheck,
    VerificationCheckResult,
    ReviewerDecisionEnum,
    RecordStatusEnum,
    AuditEvent,
    ActorEnum,
)
from app.shared.metadata import (
    get_metadata_for_family,
    FIELD_INSPECTION_METADATA,
    CUSTOMER_ONBOARDING_METADATA,
)


def test_valid_document_record():
    record = DocumentRecord(
        run_id="run-101",
        document_id="doc-001",
        document_type=DocumentType.FIELD_INSPECTION,
        document_quality=QualityResult(
            status=QualityStatus.PASS, issues=[], rescan_required=False
        ),
        field_results=[
            FieldResult(
                field_name="inspection_ref",
                display_name="Inspection Reference",
                proposed_value="INSP-2026-001",
                normalized_value="INSP-2026-001",
                confidence=0.95,
                decision=DecisionEnum.AUTO_ACCEPT,
                sensitivity=SensitivityEnum.PUBLIC,
                evidence=Evidence(
                    page=1, bounding_box=[100.0, 50.0, 150.0, 400.0]
                ),
                verification_checks=[
                    VerificationCheck(
                        rule_id="RULE-PAT-003",
                        result=VerificationCheckResult.PASS,
                        message="Pattern match success",
                    )
                ],
                decision_reason="High confidence and rules pass",
                reviewer_decision=ReviewerDecisionEnum.NOT_REQUIRED,
            )
        ],
        record_status=RecordStatusEnum.APPROVED,
        audit_events=[
            AuditEvent(
                timestamp="2026-08-29T20:00:00Z",
                actor=ActorEnum.SYSTEM,
                action="DOCUMENT_PROCESSED",
                details={"fields_processed": 1},
            )
        ],
    )

    assert record.document_id == "doc-001"
    assert record.field_results[0].confidence == 0.95
    assert record.field_results[0].evidence.bounding_box == [
        100.0,
        50.0,
        150.0,
        400.0,
    ]


def test_invalid_confidence_raises_error():
    with pytest.raises(ValidationError):
        FieldResult(
            field_name="test_field",
            display_name="Test Field",
            proposed_value="val",
            normalized_value="val",
            confidence=1.5,  # Invalid: > 1.0
            decision=DecisionEnum.AUTO_ACCEPT,
            sensitivity=SensitivityEnum.PUBLIC,
            evidence=Evidence(page=1, bounding_box=[0.0, 0.0, 10.0, 10.0]),
            decision_reason="Test",
        )


def test_invalid_bounding_box_raises_error():
    with pytest.raises(ValidationError):
        Evidence(
            page=1, bounding_box=[10.0, 20.0]
        )  # Invalid length (must be 4)


def test_metadata_dictionary_lookup():
    inspection_meta = get_metadata_for_family(DocumentType.FIELD_INSPECTION)
    assert "inspection_ref" in inspection_meta
    assert inspection_meta["inspection_ref"].required is True

    onboarding_meta = get_metadata_for_family(DocumentType.CUSTOMER_ONBOARDING)
    assert "applicant_name" in onboarding_meta
    assert onboarding_meta["applicant_name"].sensitivity == SensitivityEnum.PERSONAL
    assert onboarding_meta["applicant_name"].mandatory_human_review is True


# ────────────────────────────────────────────────────────────
# Edge-case tests added by foundation contract reconciliation
# ────────────────────────────────────────────────────────────


def test_malformed_field_result_missing_field_name():
    """Missing required property 'field_name' must raise ValidationError."""
    with pytest.raises(ValidationError):
        FieldResult(
            # field_name intentionally omitted
            display_name="Test",
            proposed_value="val",
            normalized_value="val",
            confidence=0.9,
            decision=DecisionEnum.AUTO_ACCEPT,
            sensitivity=SensitivityEnum.PUBLIC,
            evidence=Evidence(page=1, bounding_box=[0.0, 0.0, 10.0, 10.0]),
            decision_reason="Test",
        )


def test_negative_confidence_raises_error():
    """Confidence -0.5 violates minimum 0.0 constraint."""
    with pytest.raises(ValidationError):
        FieldResult(
            field_name="test_field",
            display_name="Test",
            proposed_value="val",
            normalized_value="val",
            confidence=-0.5,
            decision=DecisionEnum.AUTO_ACCEPT,
            sensitivity=SensitivityEnum.PUBLIC,
            evidence=Evidence(page=1, bounding_box=[0.0, 0.0, 10.0, 10.0]),
            decision_reason="Test",
        )


def test_auto_accept_on_personal_field_raises_error():
    """RULE-SENS-006: auto_accept + personal sensitivity must raise."""
    with pytest.raises(ValidationError, match="RULE-SENS-006"):
        FieldResult(
            field_name="applicant_name",
            display_name="Applicant Name",
            proposed_value="Jane Doe",
            normalized_value="Jane Doe",
            confidence=0.99,
            decision=DecisionEnum.AUTO_ACCEPT,
            sensitivity=SensitivityEnum.PERSONAL,
            evidence=Evidence(page=1, bounding_box=[0.0, 0.0, 10.0, 10.0]),
            decision_reason="High confidence",
        )


def test_auto_accept_on_sensitive_field_raises_error():
    """RULE-SENS-006: auto_accept + sensitive must also raise."""
    with pytest.raises(ValidationError, match="RULE-SENS-006"):
        FieldResult(
            field_name="id_ref_placeholder",
            display_name="Identity Reference",
            proposed_value="ID-*****",
            normalized_value="ID-*****",
            confidence=0.99,
            decision=DecisionEnum.AUTO_ACCEPT,
            sensitivity=SensitivityEnum.SENSITIVE,
            evidence=Evidence(page=1, bounding_box=[0.0, 0.0, 10.0, 10.0]),
            decision_reason="High confidence",
        )


def test_missing_evidence_bounding_box_raises_error():
    """Evidence without bounding_box must raise ValidationError."""
    with pytest.raises(ValidationError):
        Evidence(page=1)


def test_invalid_date_verification():
    """RULE-DATE-002: non-ISO date string must produce FAIL check."""
    from app.backend.agents.verification_agent import verify_extracted_fields

    candidates = {
        "inspection_date": {
            "proposed_value": "not-a-date",
            "confidence": 0.9,
            "sensitivity": SensitivityEnum.PUBLIC,
        }
    }
    results = verify_extracted_fields(DocumentType.FIELD_INSPECTION, candidates)
    checks, _ = results["inspection_date"]
    date_check = next(c for c in checks if c.rule_id == "RULE-DATE-002")
    assert date_check.result == VerificationCheckResult.FAIL


def test_missing_required_field_verification():
    """RULE-REQ-001: blank required field must produce FAIL check."""
    from app.backend.agents.verification_agent import verify_extracted_fields

    candidates = {
        "inspection_ref": {
            "proposed_value": "",
            "confidence": 0.5,
            "sensitivity": SensitivityEnum.PUBLIC,
        }
    }
    results = verify_extracted_fields(DocumentType.FIELD_INSPECTION, candidates)
    checks, _ = results["inspection_ref"]
    req_check = next(c for c in checks if c.rule_id == "RULE-REQ-001")
    assert req_check.result == VerificationCheckResult.FAIL


def test_unknown_document_type_returns_empty_metadata():
    """Unknown document type must return empty metadata dict."""
    meta = get_metadata_for_family(DocumentType.UNKNOWN)
    assert meta == {}


def test_invalid_audit_event_missing_actor():
    """AuditEvent without required 'actor' must raise ValidationError."""
    with pytest.raises(ValidationError):
        AuditEvent(
            timestamp="2026-08-30T12:00:00Z",
            # actor intentionally omitted
            action="TEST_ACTION",
            details={},
        )

