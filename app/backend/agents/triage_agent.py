"""
app/backend/agents/triage_agent.py — Triage & Record-Status Decision Agent

Determines field-level routing decisions (auto_accept, human_review, rescan_required)
and record-level status (awaiting_review, rescan_required, approved).

Enforces strict policy rules:
  1. Top Precedence: Quality failure / rescan_required -> rescan_required (QUALITY_CHECK_FAILED)
  2. Mandatory Sensitivity Guardrail: Personal/sensitive fields -> human_review (RULE-SENS-006)
  3. Verification Failures & Contradictions: Any failed check -> human_review (failing rule IDs)
  4. Confidence Threshold: confidence < 0.85 -> human_review (CONFIDENCE_BELOW_THRESHOLD)
  5. Auto-Accept Eligibility: Only non-sensitive, high-confidence, 100% passing fields -> auto_accept
"""

from typing import Dict, Any, List, Tuple, Optional
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
)


AGENT_VERSION = "1.4.0-triage"
CONFIGURATION_VERSION = "triage-policy-v1.0-conf0.85"
CONFIDENCE_THRESHOLD = 0.85


def run_triage_decision_stage(
    quality: QualityResult,
    candidates: Dict[str, Dict[str, Any]],
    verifications: Dict[str, Tuple[List[VerificationCheck], str]],
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> TriageResult:
    """
    Executes the decision-table policy rules across all fields and resolves overall record status.
    Returns a structured TriageResult.
    """
    field_decisions: List[FieldTriageDecision] = []
    auto_count = 0
    review_count = 0
    rescan_count = 0

    # Top Precedence: Global Quality Failure
    quality_failed = (quality.status == QualityStatus.FAIL) or quality.rescan_required

    for field_name, candidate in candidates.items():
        checks, normalized_val = verifications.get(field_name, ([], candidate.get("proposed_value")))
        confidence = float(candidate.get("confidence", 0.0))
        raw_sens = candidate.get("sensitivity", SensitivityEnum.PUBLIC)
        sensitivity = raw_sens if isinstance(raw_sens, SensitivityEnum) else SensitivityEnum(str(raw_sens))
        mandatory_review = candidate.get("mandatory_human_review", False)
        is_unreadable = candidate.get("is_unreadable", False)
        is_absent = candidate.get("is_absent", False)

        triggered: List[str] = []
        decision: DecisionEnum
        rationale: str

        # ------------------------------------------------------------------
        # Rule 1: Quality Failure Precedence
        # ------------------------------------------------------------------
        if quality_failed:
            decision = DecisionEnum.RESCAN_REQUIRED
            triggered.append("QUALITY_CHECK_FAILED")
            rationale = "Document quality check failed — rescan required."
            rescan_count += 1

        else:
            # Check all human review triggers
            if sensitivity in [SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE] or mandatory_review:
                triggered.append("RULE-SENS-006")

            failed_rules = [c.rule_id for c in checks if c.result == VerificationCheckResult.FAIL]
            for fr in failed_rules:
                if fr not in triggered:
                    triggered.append(fr)

            if is_unreadable and "UNREADABLE_FIELD" not in triggered:
                triggered.append("UNREADABLE_FIELD")
            if is_absent and "ABSENT_FIELD" not in triggered:
                triggered.append("ABSENT_FIELD")

            if confidence < confidence_threshold and "CONFIDENCE_BELOW_THRESHOLD" not in triggered:
                triggered.append("CONFIDENCE_BELOW_THRESHOLD")

            if len(triggered) > 0:
                decision = DecisionEnum.HUMAN_REVIEW
                reasons = []
                if "RULE-SENS-006" in triggered:
                    reasons.append(f"Sensitivity '{sensitivity.value}' requires human review")
                failed_msgs = [c.message for c in checks if c.result == VerificationCheckResult.FAIL]
                if failed_msgs:
                    reasons.append(f"Verification failed: {'; '.join(failed_msgs)}")
                if "CONFIDENCE_BELOW_THRESHOLD" in triggered:
                    reasons.append(f"Confidence {confidence:.2f} < {confidence_threshold:.2f}")
                if "ABSENT_FIELD" in triggered:
                    reasons.append("Field is missing")

                rationale = " | ".join(reasons) if reasons else "Field requires human review."
                review_count += 1
            else:
                decision = DecisionEnum.AUTO_ACCEPT
                triggered.append("AUTO_ACCEPT_ELIGIBLE")
                rationale = "Passed quality checks, high confidence (>=0.85), 100% passing verification rules, non-sensitive data."
                auto_count += 1

        field_decisions.append(
            FieldTriageDecision(
                field_name=field_name,
                decision=decision,
                rationale=rationale,
                triggered_rules=triggered,
                confidence=confidence,
                sensitivity=sensitivity,
            )
        )

    # ------------------------------------------------------------------
    # Record-Level Status Resolution
    # ------------------------------------------------------------------
    record_status: RecordStatusEnum
    record_rationale: str

    if quality_failed or rescan_count > 0:
        record_status = RecordStatusEnum.RESCAN_REQUIRED
        record_rationale = "Document quality check failed or scan unreadable — rescan required."
    elif review_count > 0:
        record_status = RecordStatusEnum.AWAITING_REVIEW
        record_rationale = f"Record contains {review_count} field(s) requiring human reviewer verification before export."
    else:
        record_status = RecordStatusEnum.APPROVED
        record_rationale = "All fields passed quality, confidence, and verification rules — record automatically approved."

    return TriageResult(
        agent_version=AGENT_VERSION,
        configuration_version=CONFIGURATION_VERSION,
        confidence_threshold=confidence_threshold,
        record_status=record_status,
        record_rationale=record_rationale,
        field_decisions=field_decisions,
        total_fields=len(field_decisions),
        auto_accepted_count=auto_count,
        human_review_count=review_count,
        rescan_required_count=rescan_count,
        triage_metadata={
            "quality_status": quality.status.value,
            "quality_rescan_required": quality.rescan_required,
        },
    )


# ---------------------------------------------------------------------------
# Backward-compatible helper functions (preserves existing API)
# ---------------------------------------------------------------------------
def triage_field_and_record(
    quality: QualityResult,
    confidence: float,
    sensitivity: SensitivityEnum,
    checks: List[VerificationCheck],
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> Tuple[DecisionEnum, str]:
    """
    Backward-compatible single field triage helper.
    """
    if quality.status == QualityStatus.FAIL or quality.rescan_required:
        return (
            DecisionEnum.RESCAN_REQUIRED,
            "Document quality check failed — rescan required.",
        )

    if sensitivity in [SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE]:
        return (
            DecisionEnum.HUMAN_REVIEW,
            f"Policy rule: Field sensitivity is '{sensitivity.value}'. Human review mandatory.",
        )

    has_check_failure = any(c.result == VerificationCheckResult.FAIL for c in checks)
    if has_check_failure:
        failed_msgs = [c.message for c in checks if c.result == VerificationCheckResult.FAIL]
        return (
            DecisionEnum.HUMAN_REVIEW,
            f"Verification rule check failed: {'; '.join(failed_msgs)}",
        )

    if confidence < confidence_threshold:
        return (
            DecisionEnum.HUMAN_REVIEW,
            f"Confidence {confidence:.2f} is below threshold {confidence_threshold:.2f}.",
        )

    return (
        DecisionEnum.AUTO_ACCEPT,
        "Passed quality checks, high confidence, non-sensitive data.",
    )


def determine_record_status(field_decisions: List[DecisionEnum], quality: QualityResult) -> RecordStatusEnum:
    """
    Backward-compatible record status resolution helper.
    """
    if quality.status == QualityStatus.FAIL or quality.rescan_required:
        return RecordStatusEnum.RESCAN_REQUIRED

    if any(d == DecisionEnum.RESCAN_REQUIRED for d in field_decisions):
        return RecordStatusEnum.RESCAN_REQUIRED

    if any(d == DecisionEnum.HUMAN_REVIEW for d in field_decisions):
        return RecordStatusEnum.AWAITING_REVIEW

    return RecordStatusEnum.APPROVED
