"""
tests/test_triage.py — Unit & Integration Tests for Triage & Record-Status Decision Agent

Exhaustively tests the decision-table policy rules:
  1. Quality failure precedence (QualityStatus.FAIL overrides high confidence fields -> RESCAN_REQUIRED)
  2. Confidence boundary values (0.84 -> human_review vs 0.85 -> auto_accept)
  3. Sensitive PII field enforcement (personal/sensitive fields ALWAYS route to human_review)
  4. Deterministic check failure routing (failing verification check -> human_review)
  5. Contradictions & cross-field failures (RULE-CROSS-005 -> human_review)
  6. Missing required fields (RULE-REQ-001 / ABSENT_FIELD -> human_review)
  7. Record status resolution (approved vs awaiting_review vs rescan_required)
  8. Configuration & lineage metadata tracking
  9. Backward compatibility helpers (triage_field_and_record & determine_record_status)
  10. Pipeline integration (TriageResult attached to DocumentRecord)
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("."))

from app.shared.schemas import (
    QualityResult,
    QualityStatus,
    DecisionEnum,
    SensitivityEnum,
    VerificationCheck,
    VerificationCheckResult,
    RecordStatusEnum,
    FieldTriageDecision,
    TriageResult,
    DocumentRecord,
)
from app.backend.agents.triage_agent import (
    run_triage_decision_stage,
    triage_field_and_record,
    determine_record_status,
)
from app.backend.pipeline import process_document_pipeline


def test_quality_failure_precedence():
    """QualityStatus.FAIL forces ALL fields to rescan_required, overriding 0.99 confidence."""
    quality = QualityResult(status=QualityStatus.FAIL, issues=["extreme_blur"], rescan_required=True)
    candidates = {
        "inspection_ref": {
            "proposed_value": "INSP-2026-001",
            "confidence": 0.99,
            "sensitivity": SensitivityEnum.PUBLIC,
        }
    }
    verifications = {
        "inspection_ref": ([VerificationCheck(rule_id="RULE-PAT-003", result=VerificationCheckResult.PASS, message="OK")], "INSP-2026-001")
    }

    res = run_triage_decision_stage(quality, candidates, verifications)

    assert isinstance(res, TriageResult)
    assert res.record_status == RecordStatusEnum.RESCAN_REQUIRED
    assert res.rescan_required_count == 1
    assert res.auto_accepted_count == 0

    field_dec = res.field_decisions[0]
    assert field_dec.decision == DecisionEnum.RESCAN_REQUIRED
    assert "QUALITY_CHECK_FAILED" in field_dec.triggered_rules


def test_boundary_confidence_values():
    """Confidence 0.84 routes to human_review; confidence 0.85 routes to auto_accept."""
    quality = QualityResult(status=QualityStatus.PASS, issues=[], rescan_required=False)
    verifications = {
        "site_location": ([VerificationCheck(rule_id="RULE-REQ-001", result=VerificationCheckResult.PASS, message="OK")], "Site 4")
    }

    # 0.84 -> Below threshold
    cand_84 = {
        "site_location": {"proposed_value": "Site 4", "confidence": 0.84, "sensitivity": SensitivityEnum.INTERNAL}
    }
    res_84 = run_triage_decision_stage(quality, cand_84, verifications, confidence_threshold=0.85)
    dec_84 = res_84.field_decisions[0]
    assert dec_84.decision == DecisionEnum.HUMAN_REVIEW
    assert "CONFIDENCE_BELOW_THRESHOLD" in dec_84.triggered_rules

    # 0.85 -> At threshold -> auto_accept
    cand_85 = {
        "site_location": {"proposed_value": "Site 4", "confidence": 0.85, "sensitivity": SensitivityEnum.INTERNAL}
    }
    res_85 = run_triage_decision_stage(quality, cand_85, verifications, confidence_threshold=0.85)
    dec_85 = res_85.field_decisions[0]
    assert dec_85.decision == DecisionEnum.AUTO_ACCEPT
    assert "AUTO_ACCEPT_ELIGIBLE" in dec_85.triggered_rules


def test_sensitive_pii_field_enforcement():
    """Personal and sensitive fields ALWAYS route to human_review, even with 0.99 confidence."""
    quality = QualityResult(status=QualityStatus.PASS, issues=[], rescan_required=False)
    candidates = {
        "inspector_name": {"proposed_value": "John Doe", "confidence": 0.99, "sensitivity": SensitivityEnum.PERSONAL, "mandatory_human_review": True},
        "staff_ref": {"proposed_value": "EMP-10001", "confidence": 0.99, "sensitivity": SensitivityEnum.SENSITIVE, "mandatory_human_review": True},
    }
    verifications = {
        "inspector_name": ([VerificationCheck(rule_id="RULE-REQ-001", result=VerificationCheckResult.PASS, message="OK")], "John Doe"),
        "staff_ref": ([VerificationCheck(rule_id="RULE-PAT-003", result=VerificationCheckResult.PASS, message="OK")], "EMP-10001"),
    }

    res = run_triage_decision_stage(quality, candidates, verifications)

    for dec in res.field_decisions:
        assert dec.decision == DecisionEnum.HUMAN_REVIEW
        assert "RULE-SENS-006" in dec.triggered_rules

    assert res.record_status == RecordStatusEnum.AWAITING_REVIEW
    assert res.human_review_count == 2
    assert res.auto_accepted_count == 0


def test_deterministic_check_failure_routing():
    """Any failing verification check routes field decision to human_review."""
    quality = QualityResult(status=QualityStatus.PASS, issues=[], rescan_required=False)
    candidates = {
        "inspection_date": {"proposed_value": "30-08-2026", "confidence": 0.99, "sensitivity": SensitivityEnum.PUBLIC}
    }
    verifications = {
        "inspection_date": ([
            VerificationCheck(rule_id="RULE-DATE-002", result=VerificationCheckResult.FAIL, message="failed ISO date validation")
        ], "30-08-2026")
    }

    res = run_triage_decision_stage(quality, candidates, verifications)
    dec = res.field_decisions[0]

    assert dec.decision == DecisionEnum.HUMAN_REVIEW
    assert "RULE-DATE-002" in dec.triggered_rules
    assert "failed ISO date validation" in dec.rationale


def test_contradictions_and_cross_field_failures():
    """Cross-field check failure (RULE-CROSS-005) routes affected fields to human_review."""
    quality = QualityResult(status=QualityStatus.PASS, issues=[], rescan_required=False)
    candidates = {
        "followup_date": {"proposed_value": "2026-08-01", "confidence": 0.94, "sensitivity": SensitivityEnum.PUBLIC}
    }
    verifications = {
        "followup_date": ([
            VerificationCheck(rule_id="RULE-CROSS-005", result=VerificationCheckResult.FAIL, message="Follow-up date cannot be earlier than inspection date")
        ], "2026-08-01")
    }

    res = run_triage_decision_stage(quality, candidates, verifications)
    dec = res.field_decisions[0]

    assert dec.decision == DecisionEnum.HUMAN_REVIEW
    assert "RULE-CROSS-005" in dec.triggered_rules


def test_missing_required_fields():
    """Missing required field (is_absent=True) routes to human_review."""
    quality = QualityResult(status=QualityStatus.PASS, issues=[], rescan_required=False)
    candidates = {
        "inspector_name": {"proposed_value": None, "confidence": 0.0, "sensitivity": SensitivityEnum.PERSONAL, "is_absent": True}
    }
    verifications = {
        "inspector_name": ([
            VerificationCheck(rule_id="RULE-REQ-001", result=VerificationCheckResult.FAIL, message="Mandatory field is blank or unreadable")
        ], None)
    }

    res = run_triage_decision_stage(quality, candidates, verifications)
    dec = res.field_decisions[0]

    assert dec.decision == DecisionEnum.HUMAN_REVIEW
    assert "RULE-REQ-001" in dec.triggered_rules or "ABSENT_FIELD" in dec.triggered_rules


def test_record_status_resolution():
    """Test RecordStatusEnum resolution: APPROVED vs AWAITING_REVIEW vs RESCAN_REQUIRED."""
    quality_pass = QualityResult(status=QualityStatus.PASS, issues=[], rescan_required=False)

    # 1. All non-sensitive clean fields -> APPROVED
    cand_clean = {
        "inspection_ref": {"proposed_value": "INSP-2026-001", "confidence": 0.99, "sensitivity": SensitivityEnum.PUBLIC}
    }
    verif_clean = {"inspection_ref": ([], "INSP-2026-001")}
    res_app = run_triage_decision_stage(quality_pass, cand_clean, verif_clean)
    assert res_app.record_status == RecordStatusEnum.APPROVED

    # 2. 1+ human_review fields -> AWAITING_REVIEW
    cand_review = {
        "inspector_name": {"proposed_value": "Alice", "confidence": 0.94, "sensitivity": SensitivityEnum.PERSONAL, "mandatory_human_review": True}
    }
    verif_review = {"inspector_name": ([], "Alice")}
    res_wait = run_triage_decision_stage(quality_pass, cand_review, verif_review)
    assert res_wait.record_status == RecordStatusEnum.AWAITING_REVIEW

    # 3. Quality fail -> RESCAN_REQUIRED
    quality_fail = QualityResult(status=QualityStatus.FAIL, issues=["blur"], rescan_required=True)
    res_rescan = run_triage_decision_stage(quality_fail, cand_clean, verif_clean)
    assert res_rescan.record_status == RecordStatusEnum.RESCAN_REQUIRED


def test_configuration_and_lineage_metadata():
    """Verify configuration_version and agent_version are included in TriageResult."""
    quality = QualityResult(status=QualityStatus.PASS, issues=[], rescan_required=False)
    candidates = {"ref": {"proposed_value": "123", "confidence": 0.9, "sensitivity": SensitivityEnum.PUBLIC}}
    verifs = {"ref": ([], "123")}

    res = run_triage_decision_stage(quality, candidates, verifs)
    assert res.agent_version == "1.4.0-triage"
    assert res.configuration_version == "triage-policy-v1.0-conf0.85"
    assert res.confidence_threshold == 0.85


def test_backward_compatibility_helpers():
    """Verify triage_field_and_record and determine_record_status legacy helpers."""
    quality = QualityResult(status=QualityStatus.PASS, issues=[], rescan_required=False)

    dec, msg = triage_field_and_record(
        quality=quality,
        confidence=0.99,
        sensitivity=SensitivityEnum.PUBLIC,
        checks=[VerificationCheck(rule_id="RULE-REQ-001", result=VerificationCheckResult.PASS, message="OK")],
    )
    assert dec == DecisionEnum.AUTO_ACCEPT

    status = determine_record_status([DecisionEnum.AUTO_ACCEPT, DecisionEnum.HUMAN_REVIEW], quality)
    assert status == RecordStatusEnum.AWAITING_REVIEW


def test_pipeline_integration_triage_result():
    """Pipeline attaches TriageResult to DocumentRecord."""
    record = process_document_pipeline(
        image_path="data/synthetic/field-inspection/field_insp_001.png",
        document_id="TRIAGE-PIPE-001",
        gold_data_path="data/gold-labels/FI-001_gold.json",
        doc_type_hint="field_inspection",
    )

    assert isinstance(record, DocumentRecord)
    assert record.triage_result is not None
    assert isinstance(record.triage_result, TriageResult)
    assert record.triage_result.agent_version == "1.4.0-triage"
    assert record.triage_result.configuration_version == "triage-policy-v1.0-conf0.85"
    assert record.triage_result.total_fields == 10


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------
def run_all_triage_tests():
    print("--- Running Triage & Record-Status Decision Agent Tests ---")

    test_quality_failure_precedence()
    print("[PASS] Test 1: Quality failure precedence (forces RESCAN_REQUIRED)")

    test_boundary_confidence_values()
    print("[PASS] Test 2: Boundary confidence values (0.84 -> human_review vs 0.85 -> auto_accept)")

    test_sensitive_pii_field_enforcement()
    print("[PASS] Test 3: Sensitive PII field enforcement (personal/sensitive -> human_review)")

    test_deterministic_check_failure_routing()
    print("[PASS] Test 4: Deterministic check failure routing")

    test_contradictions_and_cross_field_failures()
    print("[PASS] Test 5: Contradictions & cross-field failure routing")

    test_missing_required_fields()
    print("[PASS] Test 6: Missing required field routing")

    test_record_status_resolution()
    print("[PASS] Test 7: Record-level status resolution (APPROVED, AWAITING_REVIEW, RESCAN_REQUIRED)")

    test_configuration_and_lineage_metadata()
    print("[PASS] Test 8: Configuration & lineage metadata tracking")

    test_backward_compatibility_helpers()
    print("[PASS] Test 9: Backward compatibility helper functions")

    test_pipeline_integration_triage_result()
    print("[PASS] Test 10: Pipeline integration attaching TriageResult to DocumentRecord")

    print("\n[SUCCESS] ALL TRIAGE DECISION TESTS PASSED (10/10).")


if __name__ == "__main__":
    run_all_triage_tests()
