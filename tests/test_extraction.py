"""
tests/test_extraction.py — Unit & Integration Tests for Schema-Guided Field Extraction Agent

Validates:
  1. Complete schema coverage (100% of defined schema fields returned for each document family)
  2. Readable values (high confidence, non-null proposed_value & normalized_value)
  3. Null / absent values (missing mandatory inspector_name -> proposed_value=None, is_absent=True, confidence=0.0)
  4. Unreadable / ambiguous values (noisy text -> is_unreadable=True, confidence 0.45-0.72)
  5. Zero fabrication policy (absent fields remain None)
  6. Original vs normalized value separation
  7. Evidence locations (valid [ymin, xmin, ymax, xmax] bounding box and crop reference for every field)
  8. Agent and prompt lineage metadata tracking
  9. Unknown document type handling (returns 0 fields cleanly)
  10. Backward compatibility (extract_field_candidates helper dictionary)
  11. Pipeline integration (ExtractionResult attached to DocumentRecord)
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("."))

from app.shared.schemas import (
    DocumentType,
    FieldCandidate,
    ExtractionResult,
    DocumentRecord,
    TextStyleEnum,
)
from app.backend.agents.extraction_agent import extract_fields, extract_field_candidates
from app.backend.pipeline import process_document_pipeline


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_field_inspection_schema_coverage():
    """Test 1: Field Inspection schema coverage (10/10 expected fields)."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path="data/gold-labels/FI-001_gold.json",
        document_id="FI-001",
    )

    assert isinstance(res, ExtractionResult)
    assert res.document_type == DocumentType.FIELD_INSPECTION
    assert res.total_expected_fields == 10
    assert len(res.fields) == 10

    field_names = [f.field_name for f in res.fields]
    expected_names = [
        "inspection_ref", "inspection_date", "site_location", "inspector_name",
        "asset_ref", "inspection_status", "observation_finding", "action_required",
        "followup_date", "form_completeness"
    ]
    for name in expected_names:
        assert name in field_names, f"Missing field in extraction: {name}"


def test_customer_onboarding_schema_coverage():
    """Test 2: Customer Onboarding schema coverage (11/11 expected fields)."""
    res = extract_fields(
        image_path="data/synthetic/customer-onboarding/cust_onb_001.png",
        doc_type=DocumentType.CUSTOMER_ONBOARDING,
        gold_data_path="data/gold-labels/CO-001_gold.json",
        document_id="CO-001",
    )

    assert res.document_type == DocumentType.CUSTOMER_ONBOARDING
    assert res.total_expected_fields == 11
    assert len(res.fields) == 11

    field_names = [f.field_name for f in res.fields]
    expected_names = [
        "onboarding_ref", "application_date", "applicant_name", "contact_number",
        "email_address", "address_location", "product_requested", "id_ref_placeholder",
        "consent_indicator", "reviewer_status", "form_completeness"
    ]
    for name in expected_names:
        assert name in field_names, f"Missing field in extraction: {name}"


def test_attendance_register_schema_coverage():
    """Test 3: Attendance Register schema coverage (10/10 expected fields)."""
    res = extract_fields(
        image_path="data/test-run-01/accepted/ALL ATTENDANCE 2017-2020_1.pdf",
        doc_type=DocumentType.ATTENDANCE_REGISTER,
        gold_data_path="data/test-run-01/gold-labels/AXA-ATT-001.gold.json",
        document_id="AXA-ATT-001",
    )

    assert res.document_type == DocumentType.ATTENDANCE_REGISTER
    assert res.total_expected_fields == 10
    assert len(res.fields) == 10


def test_readable_clean_values():
    """Test 4: Clean document readable values have high confidence and non-null values."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path="data/gold-labels/FI-001_gold.json",
    )

    insp_ref = next(f for f in res.fields if f.field_name == "inspection_ref")
    assert insp_ref.proposed_value == "INSP-2026-001"
    assert insp_ref.normalized_value == "INSP-2026-001"
    assert insp_ref.confidence >= 0.98
    assert insp_ref.is_unreadable is False
    assert insp_ref.is_absent is False
    assert insp_ref.text_style == TextStyleEnum.TYPEWRITTEN


def test_null_absent_value_handling():
    """Test 5: Missing mandatory field (extreme hard case) -> proposed_value=None, is_absent=True, confidence=0.0."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_006_extreme.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path="data/gold-labels/FI-006_gold.json",
        issues=["extreme_blur", "crossed_out_text"],
    )

    inspector = next(f for f in res.fields if f.field_name == "inspector_name")
    assert inspector.proposed_value is None
    assert inspector.normalized_value is None
    assert inspector.is_absent is True
    assert inspector.confidence == 0.0


def test_unreadable_ambiguous_value_handling():
    """Test 6: Noisy/cursive text -> is_unreadable=True and confidence reduced to 0.72."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_003.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path="data/gold-labels/FI-003_gold.json",
        issues=["cursive_handwriting"],
    )

    # Handwritten field should have reduced confidence
    site_loc = next(f for f in res.fields if f.field_name == "site_location")
    assert site_loc.is_unreadable is True
    assert site_loc.confidence == 0.72


def test_zero_fabrication_policy():
    """Test 7: Confirm zero fabrication policy (unextracted/absent values remain None)."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path=None,  # No gold data provided
    )

    for field in res.fields:
        if field.proposed_value is None:
            assert field.normalized_value is None
            assert field.is_absent is True
            assert field.confidence == 0.0


def test_original_vs_normalized_value_separation():
    """Test 8: Preserves proposed_value and normalized_value separately."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path="data/gold-labels/FI-001_gold.json",
    )

    insp_ref = next(f for f in res.fields if f.field_name == "inspection_ref")
    assert hasattr(insp_ref, "proposed_value")
    assert hasattr(insp_ref, "normalized_value")
    assert insp_ref.proposed_value == insp_ref.normalized_value


def test_evidence_location_references():
    """Test 9: Every candidate carries valid page=1, 4-element bounding box, and crop reference."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path="data/gold-labels/FI-001_gold.json",
        document_id="FI-001",
    )

    for field in res.fields:
        assert field.evidence.page == 1
        assert len(field.evidence.bounding_box) == 4
        assert field.evidence.crop_reference == f"/crops/FI-001_{field.field_name}.png"


def test_agent_and_prompt_lineage_metadata():
    """Test 10: ExtractionResult includes agent_version, prompt_version_id, and adapter_type."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path="data/gold-labels/FI-001_gold.json",
    )

    assert res.agent_version == "1.2.0-extraction"
    assert res.prompt_version_id == "prompt-schema-guided-v1.0"
    assert res.adapter_type in ["synthetic_test_adapter", "vlm_vision_api"]
    assert "zero_fabrication_enforced" in res.extraction_metadata


def test_unknown_document_type_handling():
    """Test 11: Unknown document type returns 0 fields cleanly without raising errors."""
    res = extract_fields(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        doc_type=DocumentType.UNKNOWN,
    )

    assert res.document_type == DocumentType.UNKNOWN
    assert res.total_expected_fields == 0
    assert len(res.fields) == 0


def test_backward_compatibility_candidates_dict():
    """Test 12: extract_field_candidates() returns backward-compatible candidate dict."""
    candidates = extract_field_candidates(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        doc_type=DocumentType.FIELD_INSPECTION,
        gold_data_path="data/gold-labels/FI-001_gold.json",
    )

    assert isinstance(candidates, dict)
    assert len(candidates) == 10
    assert "inspection_ref" in candidates
    assert candidates["inspection_ref"]["proposed_value"] == "INSP-2026-001"
    assert "mandatory_human_review" in candidates["inspection_ref"]


def test_pipeline_integration_extraction_result():
    """Test 13: Pipeline attaches ExtractionResult to DocumentRecord."""
    record = process_document_pipeline(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        document_id="EXTRACT-PIPE-001",
        gold_data_path="data/gold-labels/FI-001_gold.json",
        doc_type_hint="field_inspection",
    )

    assert isinstance(record, DocumentRecord)
    assert record.extraction_result is not None
    assert isinstance(record.extraction_result, ExtractionResult)
    assert record.extraction_result.agent_version == "1.2.0-extraction"
    assert record.extraction_result.total_expected_fields == 10


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------
def run_all_extraction_tests():
    print("--- Running Schema-Guided Field Extraction Agent Tests ---")

    test_field_inspection_schema_coverage()
    print("[PASS] Test 1: Field Inspection schema coverage (10/10 fields)")

    test_customer_onboarding_schema_coverage()
    print("[PASS] Test 2: Customer Onboarding schema coverage (11/11 fields)")

    test_attendance_register_schema_coverage()
    print("[PASS] Test 3: Attendance Register schema coverage (10/10 fields)")

    test_readable_clean_values()
    print("[PASS] Test 4: Clean document readable values extraction")

    test_null_absent_value_handling()
    print("[PASS] Test 5: Missing mandatory field null value & zero confidence handling")

    test_unreadable_ambiguous_value_handling()
    print("[PASS] Test 6: Unreadable / noisy handwriting handling")

    test_zero_fabrication_policy()
    print("[PASS] Test 7: Zero fabrication policy (unextracted values remain None)")

    test_original_vs_normalized_value_separation()
    print("[PASS] Test 8: Proposed vs normalized value separation")

    test_evidence_location_references()
    print("[PASS] Test 9: Evidence bounding boxes and crop reference URIs")

    test_agent_and_prompt_lineage_metadata()
    print("[PASS] Test 10: Agent & prompt lineage metadata tracking")

    test_unknown_document_type_handling()
    print("[PASS] Test 11: Unknown document type handling (0 fields cleanly)")

    test_backward_compatibility_candidates_dict()
    print("[PASS] Test 12: Backward compatibility helper function")

    test_pipeline_integration_extraction_result()
    print("[PASS] Test 13: Pipeline integration attaching ExtractionResult to DocumentRecord")

    print("\n[SUCCESS] ALL SCHEMA-GUIDED EXTRACTION TESTS PASSED (13/13).")


if __name__ == "__main__":
    run_all_extraction_tests()
