import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.shared.schemas import DocumentType, QualityStatus, RecordStatusEnum, DecisionEnum, SensitivityEnum
from app.backend.pipeline import process_document_pipeline


def test_clean_document_routing():
    # FI-001 clean sample
    image_path = "data/synthetic/field-inspection/field_insp_001.png"
    gold_path = "data/gold-labels/FI-001_gold.json"

    record = process_document_pipeline(
        image_path=image_path,
        document_id="FI-001",
        gold_data_path=gold_path,
        doc_type_hint="field_inspection",
    )

    assert record.document_type == DocumentType.FIELD_INSPECTION
    assert record.document_quality.status == QualityStatus.PASS
    # inspector_name is personal -> mandatory human_review
    # non-sensitive high confidence fields -> auto_accept
    inspector_field = next(f for f in record.field_results if f.field_name == "inspector_name")
    assert inspector_field.decision == DecisionEnum.HUMAN_REVIEW

    ref_field = next(f for f in record.field_results if f.field_name == "inspection_ref")
    assert ref_field.decision == DecisionEnum.AUTO_ACCEPT


def test_extreme_hard_case_routing():
    # FI-006 extreme hard case (blur, skew, missing inspector_name)
    image_path = "data/synthetic/field-inspection/field_insp_006_extreme.png"
    gold_path = "data/gold-labels/FI-006_gold.json"

    record = process_document_pipeline(
        image_path=image_path,
        document_id="FI-006",
        gold_data_path=gold_path,
        issues_hint=["extreme_blur", "skew", "crossed_out_text"],
        doc_type_hint="field_inspection",
    )

    assert record.document_quality.status == QualityStatus.FAIL
    assert record.document_quality.rescan_required is True
    assert record.record_status == RecordStatusEnum.RESCAN_REQUIRED


def test_sensitive_customer_onboarding_routing():
    # CO-001 onboarding sample (PII fields must route to human_review)
    image_path = "data/synthetic/customer-onboarding/cust_onb_001.png"
    gold_path = "data/gold-labels/CO-001_gold.json"

    record = process_document_pipeline(
        image_path=image_path,
        document_id="CO-001",
        gold_data_path=gold_path,
        doc_type_hint="customer_onboarding",
    )

    assert record.record_status == RecordStatusEnum.AWAITING_REVIEW

    # Verify PII fields (applicant_name, contact_number, address_location, id_ref_placeholder) routed to human_review
    sensitive_fields = ["applicant_name", "contact_number", "address_location", "id_ref_placeholder"]
    for f_name in sensitive_fields:
        f_obj = next(f for f in record.field_results if f.field_name == f_name)
        assert f_obj.decision == DecisionEnum.HUMAN_REVIEW
        assert f_obj.sensitivity in [SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE]


def test_typewritten_text_processing():
    image_path = "data/synthetic/field-inspection/field_insp_001.png"
    gold_path = "data/gold-labels/FI-001_gold.json"

    record = process_document_pipeline(
        image_path=image_path,
        document_id="FI-001-TYPED",
        gold_data_path=gold_path,
        issues_hint=["typewritten"],
        doc_type_hint="field_inspection",
    )

    # Typewritten field inspection_ref should have high confidence (0.99) and typewritten text_style
    ref_field = next(f for f in record.field_results if f.field_name == "inspection_ref")
    assert ref_field.text_style.value == "typewritten"
    assert ref_field.confidence >= 0.98
    assert ref_field.decision == DecisionEnum.AUTO_ACCEPT


def run_all_pipeline_tests():
    print("--- Running Agent Pipeline Integration Tests ---")
    test_clean_document_routing()
    print("[PASS] Clean Document Pipeline Test")
    test_extreme_hard_case_routing()
    print("[PASS] Extreme Hard Case Rescan Routing Test")
    test_sensitive_customer_onboarding_routing()
    print("[PASS] Sensitive PII Mandatory Human Review Test")
    test_typewritten_text_processing()
    print("[PASS] Graceful Typewritten Text Processing Test")
    print("\n[SUCCESS] ALL AGENT PIPELINE TESTS PASSED CLEANLY (4/4).")


if __name__ == "__main__":
    run_all_pipeline_tests()
