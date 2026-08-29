from typing import Dict, Any, List, Tuple
from app.shared.schemas import (
    QualityResult,
    QualityStatus,
    DecisionEnum,
    SensitivityEnum,
    VerificationCheck,
    VerificationCheckResult,
    RecordStatusEnum,
)


def triage_field_and_record(
    quality: QualityResult,
    confidence: float,
    sensitivity: SensitivityEnum,
    checks: List[VerificationCheck],
    confidence_threshold: float = 0.85,
) -> Tuple[DecisionEnum, str]:
    """
    Triage Agent:
    Determines auto_accept, human_review, or rescan_required per field.

    Policy:
    - Quality FAIL -> rescan_required
    - Sensitivity personal/sensitive -> human_review (mandatory human sign-off)
    - Confidence < confidence_threshold -> human_review
    - Any verification check FAIL -> human_review
    - Non-sensitive, high confidence, 100% passing checks -> auto_accept
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
    if quality.status == QualityStatus.FAIL or quality.rescan_required:
        return RecordStatusEnum.RESCAN_REQUIRED

    if any(d == DecisionEnum.RESCAN_REQUIRED for d in field_decisions):
        return RecordStatusEnum.RESCAN_REQUIRED

    if any(d == DecisionEnum.HUMAN_REVIEW for d in field_decisions):
        return RecordStatusEnum.AWAITING_REVIEW

    return RecordStatusEnum.APPROVED
