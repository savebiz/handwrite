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
