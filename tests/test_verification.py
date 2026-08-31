"""
tests/test_verification.py — Unit & Integration Tests for Deterministic Verification Agent

Validates all 9 deterministic verification rules:
  1. RULE-REQ-001: Required field check (PASS on present, FAIL on blank/missing)
  2. RULE-DATE-002: ISO-8601 date parsing & future date validation (FAIL on invalid format or future date)
  3. RULE-PAT-003: Pattern match / reference number regex (FAIL on invalid pattern)
  4. RULE-VOCAB-004: Controlled vocabulary enum check (FAIL on invalid enum)
  5. RULE-CONSENT-007: Consent indicator validation (FAIL on invalid consent e.g. "MAYBE")
  6. RULE-SENS-006: Sensitivity policy guardrail (WARNING result for human review routing)
  7. RULE-CROSS-005: Cross-field consistency (FAIL if followup_date < inspection_date or time_out < time_in)
  8. RULE-MISSING-008: Missing/conflicting form completeness (FAIL if COMPLETE but required field missing)
  9. RULE-NORM-009: Original value preservation & transformation tracking (proposed_value untouched)
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("."))

from app.shared.schemas import (
    DocumentType,
    VerificationCheck,
    VerificationCheckResult,
    VerificationResult,
    DocumentRecord,
    Evidence,
)
from app.backend.agents.verification_agent import (
    run_deterministic_verification,
    verify_extracted_fields,
)
from app.backend.pipeline import process_document_pipeline


def test_rule_req_001_required_field_check():
    """RULE-REQ-001: PASS on present required field, FAIL on missing required field."""
    candidates = {
        "inspection_ref": {"proposed_value": "INSP-2026-001"},
        "inspector_name": {"proposed_value": None},  # Missing required field
    }

    res = run_deterministic_verification(DocumentType.FIELD_INSPECTION, candidates)

    ref_req_check = next(c for c in res.field_checks["inspection_ref"] if c.rule_id == "RULE-REQ-001")
    assert ref_req_check.result == VerificationCheckResult.PASS
    assert ref_req_check.field_name == "inspection_ref"

    insp_req_check = next(c for c in res.field_checks["inspector_name"] if c.rule_id == "RULE-REQ-001")
    assert insp_req_check.result == VerificationCheckResult.FAIL
    assert insp_req_check.field_name == "inspector_name"
    assert "blank or unreadable" in insp_req_check.message


def test_rule_date_002_iso_date_and_future_validation():
    """RULE-DATE-002: PASS on valid date, FAIL on malformed date or future date."""
    candidates = {
        "inspection_date": {"proposed_value": "2026-08-30"},
        "followup_date": {"proposed_value": "30-08-2026"},   # Malformed format
    }

    res = run_deterministic_verification(DocumentType.FIELD_INSPECTION, candidates)

    date_pass = next(c for c in res.field_checks["inspection_date"] if c.rule_id == "RULE-DATE-002")
    assert date_pass.result == VerificationCheckResult.PASS

    date_fail = next(c for c in res.field_checks["followup_date"] if c.rule_id == "RULE-DATE-002")
    assert date_fail.result == VerificationCheckResult.FAIL
    assert "failed ISO date validation" in date_fail.message

    # Test future date failure
    future_candidates = {
        "inspection_date": {"proposed_value": "2099-01-01"},  # Future date
    }
    fut_res = run_deterministic_verification(DocumentType.FIELD_INSPECTION, future_candidates)
    fut_check = next(c for c in fut_res.field_checks["inspection_date"] if c.rule_id == "RULE-DATE-002")
    assert fut_check.result == VerificationCheckResult.FAIL
    assert "cannot be in the future" in fut_check.message


def test_rule_pat_003_pattern_matching():
    """RULE-PAT-003: PASS on valid pattern, FAIL on invalid pattern."""
    candidates = {
        "inspection_ref": {"proposed_value": "INSP-2026-001"},  # Valid
        "asset_ref": {"proposed_value": "INVALID-AST-123"},     # Invalid
    }

    res = run_deterministic_verification(DocumentType.FIELD_INSPECTION, candidates)

    pass_pat = next(c for c in res.field_checks["inspection_ref"] if c.rule_id == "RULE-PAT-003")
    assert pass_pat.result == VerificationCheckResult.PASS

    fail_pat = next(c for c in res.field_checks["asset_ref"] if c.rule_id == "RULE-PAT-003")
    assert fail_pat.result == VerificationCheckResult.FAIL
    assert "does not match pattern" in fail_pat.message


def test_rule_vocab_004_controlled_vocabulary():
    """RULE-VOCAB-004: PASS on allowed enum value, FAIL on invalid enum value."""
    candidates = {
        "inspection_status": {"proposed_value": "PASS"},               # Valid
        "form_completeness": {"proposed_value": "INVALID_ENUM_VAL"},    # Invalid
    }

    res = run_deterministic_verification(DocumentType.FIELD_INSPECTION, candidates)

    vocab_pass = next(c for c in res.field_checks["inspection_status"] if c.rule_id == "RULE-VOCAB-004")
    assert vocab_pass.result == VerificationCheckResult.PASS

    vocab_fail = next(c for c in res.field_checks["form_completeness"] if c.rule_id == "RULE-VOCAB-004")
    assert vocab_fail.result == VerificationCheckResult.FAIL
    assert "not in allowed enums" in vocab_fail.message


def test_rule_consent_007_consent_indicator():
    """RULE-CONSENT-007: PASS on 'YES'/'NO', FAIL on invalid consent value like 'MAYBE'."""
    valid_candidates = {"consent_indicator": {"proposed_value": "YES"}}
    invalid_candidates = {"consent_indicator": {"proposed_value": "MAYBE"}}

    res_valid = run_deterministic_verification(DocumentType.CUSTOMER_ONBOARDING, valid_candidates)
    chk_valid = next(c for c in res_valid.field_checks["consent_indicator"] if c.rule_id == "RULE-CONSENT-007")
    assert chk_valid.result == VerificationCheckResult.PASS

    res_invalid = run_deterministic_verification(DocumentType.CUSTOMER_ONBOARDING, invalid_candidates)
    chk_invalid = next(c for c in res_invalid.field_checks["consent_indicator"] if c.rule_id == "RULE-CONSENT-007")
    assert chk_invalid.result == VerificationCheckResult.FAIL
    assert "must be 'YES' or 'NO'" in chk_invalid.message


def test_rule_sens_006_sensitivity_policy_warning():
    """RULE-SENS-006: Personal and sensitive fields emit WARNING check."""
    candidates = {
        "applicant_name": {"proposed_value": "John Doe"},
        "id_ref_placeholder": {"proposed_value": "ID-12345"},
    }

    res = run_deterministic_verification(DocumentType.CUSTOMER_ONBOARDING, candidates)

    sens_name = next(c for c in res.field_checks["applicant_name"] if c.rule_id == "RULE-SENS-006")
    assert sens_name.result == VerificationCheckResult.WARNING
    assert "mandatory human review required" in sens_name.message

    sens_id = next(c for c in res.field_checks["id_ref_placeholder"] if c.rule_id == "RULE-SENS-006")
    assert sens_id.result == VerificationCheckResult.WARNING


def test_rule_cross_005_cross_field_consistency():
    """RULE-CROSS-005: FAIL when followup_date < inspection_date or time_out < time_in."""
    # Inspection cross-field test
    insp_candidates = {
        "inspection_date": {"proposed_value": "2026-08-30"},
        "followup_date": {"proposed_value": "2026-08-01"},  # Followup before inspection
    }

    res_insp = run_deterministic_verification(DocumentType.FIELD_INSPECTION, insp_candidates)
    cross_insp = next(c for c in res_insp.field_checks.get("followup_date", []) if c.rule_id == "RULE-CROSS-005")
    assert cross_insp.result == VerificationCheckResult.FAIL
    assert "cannot be earlier" in cross_insp.message

    # Attendance cross-field test
    att_candidates = {
        "time_in": {"proposed_value": "17:00"},
        "time_out": {"proposed_value": "09:00"},  # Time out before time in
    }

    res_att = run_deterministic_verification(DocumentType.ATTENDANCE_REGISTER, att_candidates)
    cross_att = next(c for c in res_att.field_checks.get("time_out", []) if c.rule_id == "RULE-CROSS-005")
    assert cross_att.result == VerificationCheckResult.FAIL
    assert "Time out cannot be earlier than time in" in cross_att.message


def test_rule_missing_008_form_completeness_conflict():
    """RULE-MISSING-008: FAIL if form_completeness == COMPLETE but required fields missing."""
    candidates = {
        "form_completeness": {"proposed_value": "COMPLETE"},
        "inspector_name": {"proposed_value": None},  # Missing required field
    }

    res = run_deterministic_verification(DocumentType.FIELD_INSPECTION, candidates)
    missing_check = next(c for c in res.field_checks.get("inspector_name", []) if c.rule_id == "RULE-MISSING-008")
    assert missing_check.result == VerificationCheckResult.FAIL
    assert "Form marked COMPLETE but required field" in missing_check.message


def test_rule_norm_009_original_value_preservation_and_transformations():
    """RULE-NORM-009: Raw proposed_value remains untouched while normalized_value is cleaned."""
    candidates = {
        "site_location": {"proposed_value": "  North Building Site 4  "},  # Extra padding
    }

    res = run_deterministic_verification(DocumentType.FIELD_INSPECTION, candidates)

    assert candidates["site_location"]["proposed_value"] == "  North Building Site 4  "  # Raw untouched
    assert res.normalized_values["site_location"] == "North Building Site 4"               # Cleaned

    # Verify transformation record
    assert len(res.value_transformations) >= 1
    trans = next(t for t in res.value_transformations if t["field_name"] == "site_location")
    assert trans["original_value"] == "  North Building Site 4  "
    assert trans["normalized_value"] == "North Building Site 4"
    assert trans["rule_id"] == "RULE-NORM-009"


def test_field_name_included_in_checks():
    """Every VerificationCheck includes the target field_name."""
    candidates = {
        "inspection_ref": {"proposed_value": "INSP-2026-001"},
    }

    res = run_deterministic_verification(DocumentType.FIELD_INSPECTION, candidates)

    for chk in res.checks:
        assert chk.field_name is not None
        assert chk.field_name == "inspection_ref"


def test_backward_compatibility_verify_extracted_fields():
    """verify_extracted_fields() returns legacy Dict[field_name, Tuple[checks, normalized_val]]."""
    candidates = {
        "inspection_ref": {"proposed_value": "INSP-2026-001"},
    }

    legacy_res = verify_extracted_fields(DocumentType.FIELD_INSPECTION, candidates)

    assert isinstance(legacy_res, dict)
    assert "inspection_ref" in legacy_res
    checks, norm_val = legacy_res["inspection_ref"]
    assert isinstance(checks, list)
    assert norm_val == "INSP-2026-001"


def test_rule_evid_010_field_evidence_verification():
    """RULE-EVID-010 verifies bounding_box is valid non-zero rectangle."""
    cand_valid = {
        "inspection_ref": {
            "proposed_value": "INSP-2026-001",
            "evidence": Evidence(page=1, bounding_box=[100, 200, 150, 400], crop_reference="/crops/test.png"),
        }
    }
    res_v = run_deterministic_verification(DocumentType.FIELD_INSPECTION, cand_valid)
    chk_v = next(c for c in res_v.checks if c.rule_id == "RULE-EVID-010")
    assert chk_v.result == VerificationCheckResult.PASS

    cand_invalid = {
        "inspection_ref": {
            "proposed_value": "INSP-2026-001",
            "evidence": Evidence(page=1, bounding_box=[0, 0, 0, 0], crop_reference="/crops/test.png"),
        }
    }
    res_inv = run_deterministic_verification(DocumentType.FIELD_INSPECTION, cand_invalid)
    chk_inv = next(c for c in res_inv.checks if c.rule_id == "RULE-EVID-010")
    assert chk_inv.result == VerificationCheckResult.FAIL


def test_pipeline_integration_verification_result():
    """Pipeline attaches VerificationResult to DocumentRecord."""
    record = process_document_pipeline(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        document_id="VERIFY-PIPE-001",
        gold_data_path="data/gold-labels/FI-001_gold.json",
        doc_type_hint="field_inspection",
    )

    assert isinstance(record, DocumentRecord)
    assert record.verification_result is not None
    assert isinstance(record.verification_result, VerificationResult)
    assert record.verification_result.agent_version == "1.3.0-verification"
    assert record.verification_result.total_checks_run > 0


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------
def run_all_verification_tests():
    print("--- Running Deterministic Verification Agent Tests ---")

    test_rule_req_001_required_field_check()
    print("[PASS] Test 1: RULE-REQ-001 Required field check (PASS / FAIL)")

    test_rule_date_002_iso_date_and_future_validation()
    print("[PASS] Test 2: RULE-DATE-002 ISO date format & future date validation")

    test_rule_pat_003_pattern_matching()
    print("[PASS] Test 3: RULE-PAT-003 Reference pattern matching")

    test_rule_vocab_004_controlled_vocabulary()
    print("[PASS] Test 4: RULE-VOCAB-004 Controlled vocabulary enum check")

    test_rule_consent_007_consent_indicator()
    print("[PASS] Test 5: RULE-CONSENT-007 Consent indicator check (YES/NO)")

    test_rule_sens_006_sensitivity_policy_warning()
    print("[PASS] Test 6: RULE-SENS-006 Sensitivity policy warning check")

    test_rule_cross_005_cross_field_consistency()
    print("[PASS] Test 7: RULE-CROSS-005 Cross-field date & time consistency")

    test_rule_missing_008_form_completeness_conflict()
    print("[PASS] Test 8: RULE-MISSING-008 Missing/conflicting completeness check")

    test_rule_norm_009_original_value_preservation_and_transformations()
    print("[PASS] Test 9: RULE-NORM-009 Original value preservation & transformation tracking")

    test_rule_evid_010_field_evidence_verification()
    print("[PASS] Test 10: RULE-EVID-010 Field evidence bounding box verification")

    test_field_name_included_in_checks()
    print("[PASS] Test 11: field_name included in all VerificationCheck objects")

    test_backward_compatibility_verify_extracted_fields()
    print("[PASS] Test 12: Backward-compatible verify_extracted_fields helper")

    test_pipeline_integration_verification_result()
    print("[PASS] Test 13: Pipeline integration attaching VerificationResult to DocumentRecord")

    print("\n[SUCCESS] ALL DETERMINISTIC VERIFICATION TESTS PASSED (13/13).")


if __name__ == "__main__":
    run_all_verification_tests()
