import sys
import os

# Add local directories to sys.path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

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


def run_tests():
    print("--- Running Schema & Data Contract Unit Tests ---")

    # Test 1: Valid DocumentRecord
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
    print("[PASS] Test 1: Valid DocumentRecord creation and validation")

    # Test 2: Invalid Confidence (> 1.0)
    try:
        FieldResult(
            field_name="test_field",
            display_name="Test Field",
            proposed_value="val",
            normalized_value="val",
            confidence=1.5,  # Invalid
            decision=DecisionEnum.AUTO_ACCEPT,
            sensitivity=SensitivityEnum.PUBLIC,
            evidence=Evidence(page=1, bounding_box=[0.0, 0.0, 10.0, 10.0]),
            decision_reason="Test",
        )
        print("[FAIL] Test 2: Invalid confidence should have raised ValidationError")
        sys.exit(1)
    except ValidationError:
        print("[PASS] Test 2: Correctly rejected invalid confidence > 1.0")

    # Test 3: Invalid Bounding Box length
    try:
        Evidence(page=1, bounding_box=[10.0, 20.0])  # Must have length 4
        print("[FAIL] Test 3: Invalid bounding box length should have raised ValidationError")
        sys.exit(1)
    except ValidationError:
        print("[PASS] Test 3: Correctly rejected invalid bounding box length")

    # Test 4: Metadata Dictionary Lookup
    inspection_meta = get_metadata_for_family(DocumentType.FIELD_INSPECTION)
    assert "inspection_ref" in inspection_meta
    assert inspection_meta["inspection_ref"].required is True
    print("[PASS] Test 4: Field inspection metadata lookup")

    onboarding_meta = get_metadata_for_family(DocumentType.CUSTOMER_ONBOARDING)
    assert "applicant_name" in onboarding_meta
    assert onboarding_meta["applicant_name"].sensitivity == SensitivityEnum.PERSONAL
    assert onboarding_meta["applicant_name"].mandatory_human_review is True
    print("[PASS] Test 5: Customer onboarding metadata lookup & mandatory review flag")

    print("\n[SUCCESS] ALL SCHEMA VALIDATION TESTS PASSED CLEANLY (5/5).")


if __name__ == "__main__":
    run_tests()
