import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
from app.shared.schemas import DocumentType, VerificationCheck, VerificationCheckResult, SensitivityEnum
from app.shared.metadata import get_metadata_for_family


def verify_extracted_fields(
    doc_type: DocumentType, extracted_candidates: Dict[str, Dict[str, Any]]
) -> Dict[str, Tuple[List[VerificationCheck], str]]:
    """
    Deterministic Verification Agent:
    Enforces regex patterns, valid dates, required fields, enum vocabulary, cross-field consistency,
    and sensitivity flags BEFORE model judgment.
    """
    meta_dict = get_metadata_for_family(doc_type)
    results = {}

    for field_name, candidate in extracted_candidates.items():
        meta = meta_dict.get(field_name)
        checks: List[VerificationCheck] = []
        proposed = candidate.get("proposed_value")
        normalized = proposed

        if not meta:
            results[field_name] = (checks, normalized)
            continue

        # RULE-REQ-001: Required Field Check
        if meta.required:
            if proposed is None or str(proposed).strip() == "":
                checks.append(
                    VerificationCheck(
                        rule_id="RULE-REQ-001",
                        result=VerificationCheckResult.FAIL,
                        message=f"Mandatory field '{meta.display_name}' is blank or unreadable.",
                    )
                )
            else:
                checks.append(
                    VerificationCheck(
                        rule_id="RULE-REQ-001",
                        result=VerificationCheckResult.PASS,
                        message="Required field present.",
                    )
                )

        # RULE-DATE-002: ISO-8601 Date Parsing
        if meta.data_type == "date" and proposed:
            try:
                dt = datetime.strptime(str(proposed), "%Y-%m-%d")
                normalized = dt.strftime("%Y-%m-%d")
                checks.append(
                    VerificationCheck(
                        rule_id="RULE-DATE-002",
                        result=VerificationCheckResult.PASS,
                        message="Valid ISO-8601 date string.",
                    )
                )
            except ValueError:
                checks.append(
                    VerificationCheck(
                        rule_id="RULE-DATE-002",
                        result=VerificationCheckResult.FAIL,
                        message=f"Value '{proposed}' failed ISO date validation (YYYY-MM-DD).",
                    )
                )

        # RULE-PAT-003: Regex Pattern Matching
        if meta.pattern and proposed:
            if re.match(meta.pattern, str(proposed)):
                checks.append(
                    VerificationCheck(
                        rule_id="RULE-PAT-003",
                        result=VerificationCheckResult.PASS,
                        message=f"Matches pattern '{meta.pattern}'.",
                    )
                )
            else:
                checks.append(
                    VerificationCheck(
                        rule_id="RULE-PAT-003",
                        result=VerificationCheckResult.FAIL,
                        message=f"Value '{proposed}' does not match pattern '{meta.pattern}'.",
                    )
                )

        # RULE-VOCAB-004: Controlled Vocabulary
        if meta.allowed_values and proposed:
            if str(proposed) in meta.allowed_values:
                checks.append(
                    VerificationCheck(
                        rule_id="RULE-VOCAB-004",
                        result=VerificationCheckResult.PASS,
                        message="Value in controlled vocabulary.",
                    )
                )
            else:
                checks.append(
                    VerificationCheck(
                        rule_id="RULE-VOCAB-004",
                        result=VerificationCheckResult.FAIL,
                        message=f"Value '{proposed}' not in allowed enums: {meta.allowed_values}.",
                    )
                )

        # RULE-SENS-006: Sensitivity Guardrail
        if meta.sensitivity in [SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE] or meta.mandatory_human_review:
            checks.append(
                VerificationCheck(
                    rule_id="RULE-SENS-006",
                    result=VerificationCheckResult.WARNING,
                    message=f"Field classified as '{meta.sensitivity.value}' — mandatory human review required.",
                )
            )

        results[field_name] = (checks, normalized)

    # RULE-CROSS-005: Cross-field Followup Date Check for field_inspection
    if doc_type == DocumentType.FIELD_INSPECTION:
        insp_date_str = extracted_candidates.get("inspection_date", {}).get("proposed_value")
        follow_date_str = extracted_candidates.get("followup_date", {}).get("proposed_value")

        if insp_date_str and follow_date_str:
            try:
                dt_insp = datetime.strptime(str(insp_date_str), "%Y-%m-%d")
                dt_follow = datetime.strptime(str(follow_date_str), "%Y-%m-%d")
                if dt_follow < dt_insp:
                    checks, norm = results.get("followup_date", ([], follow_date_str))
                    checks.append(
                        VerificationCheck(
                            rule_id="RULE-CROSS-005",
                            result=VerificationCheckResult.FAIL,
                            message="Follow-up date cannot be earlier than inspection date.",
                        )
                    )
                    results["followup_date"] = (checks, norm)
            except ValueError:
                pass

    return results
