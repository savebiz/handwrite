"""
app/backend/agents/verification_agent.py — Deterministic Verification Agent

Enforces 9 deterministic verification rules before model judgment or triage:
  1. RULE-REQ-001: Required field check
  2. RULE-DATE-002: ISO-8601 Date parsing and future date validation
  3. RULE-PAT-003: Pattern match / reference-number regex validation
  4. RULE-VOCAB-004: Controlled vocabulary enum membership check
  5. RULE-CONSENT-007: Consent indicator validation (YES/NO)
  6. RULE-SENS-006: Sensitivity policy guardrail
  7. RULE-CROSS-005: Cross-field date & time logical consistency
  8. RULE-MISSING-008: Missing/conflicting form completeness check
  9. RULE-NORM-009: Normalized-value validity and transformation tracking

Strictly enforces:
  - Original proposed_value is NEVER overwritten
  - Transformations are recorded explicitly in value_transformations
"""

import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional

from app.shared.schemas import (
    DocumentType,
    VerificationCheck,
    VerificationCheckResult,
    VerificationResult,
    SensitivityEnum,
)
from app.shared.metadata import get_metadata_for_family


AGENT_VERSION = "1.3.0-verification"


def run_deterministic_verification(
    doc_type: DocumentType,
    extracted_candidates: Dict[str, Dict[str, Any]],
) -> VerificationResult:
    """
    Executes all 9 deterministic verification checks on extracted field candidates.
    Returns a structured VerificationResult containing checks, normalized values,
    and recorded value transformations.
    """
    meta_dict = get_metadata_for_family(doc_type)
    all_checks: List[VerificationCheck] = []
    field_checks_map: Dict[str, List[VerificationCheck]] = {}
    normalized_map: Dict[str, Optional[str]] = {}
    transformations: List[Dict[str, Any]] = []

    passed_count = 0
    failed_count = 0
    warning_count = 0

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for field_name, candidate in extracted_candidates.items():
        meta = meta_dict.get(field_name)
        f_checks: List[VerificationCheck] = []
        proposed = candidate.get("proposed_value")
        normalized = proposed

        if not meta:
            field_checks_map[field_name] = f_checks
            normalized_map[field_name] = normalized
            continue

        # ------------------------------------------------------------------
        # RULE-REQ-001: Required Field Check
        # ------------------------------------------------------------------
        if meta.required:
            if proposed is None or str(proposed).strip() == "":
                chk = VerificationCheck(
                    rule_id="RULE-REQ-001",
                    result=VerificationCheckResult.FAIL,
                    message=f"Mandatory field '{meta.display_name}' is blank or unreadable.",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                failed_count += 1
            else:
                chk = VerificationCheck(
                    rule_id="RULE-REQ-001",
                    result=VerificationCheckResult.PASS,
                    message=f"Required field '{meta.display_name}' present.",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                passed_count += 1

        # ------------------------------------------------------------------
        # RULE-DATE-002: ISO-8601 Date Parsing & Future Date Validation
        # ------------------------------------------------------------------
        if meta.data_type == "date" and proposed and str(proposed).strip():
            raw_str = str(proposed).strip()
            try:
                dt = datetime.strptime(raw_str, "%Y-%m-%d")
                iso_formatted = dt.strftime("%Y-%m-%d")

                if iso_formatted > today_str:
                    chk = VerificationCheck(
                        rule_id="RULE-DATE-002",
                        result=VerificationCheckResult.FAIL,
                        message=f"Date '{raw_str}' cannot be in the future (current date: {today_str}).",
                        field_name=field_name,
                    )
                    f_checks.append(chk)
                    all_checks.append(chk)
                    failed_count += 1
                else:
                    normalized = iso_formatted
                    chk = VerificationCheck(
                        rule_id="RULE-DATE-002",
                        result=VerificationCheckResult.PASS,
                        message="Valid ISO-8601 date string.",
                        field_name=field_name,
                    )
                    f_checks.append(chk)
                    all_checks.append(chk)
                    passed_count += 1
            except ValueError:
                chk = VerificationCheck(
                    rule_id="RULE-DATE-002",
                    result=VerificationCheckResult.FAIL,
                    message=f"Value '{proposed}' failed ISO date validation (YYYY-MM-DD).",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                failed_count += 1

        # ------------------------------------------------------------------
        # RULE-PAT-003: Regex Pattern Matching / Reference Number Format
        # ------------------------------------------------------------------
        if meta.pattern and proposed and str(proposed).strip():
            raw_str = str(proposed).strip()
            if re.match(meta.pattern, raw_str):
                chk = VerificationCheck(
                    rule_id="RULE-PAT-003",
                    result=VerificationCheckResult.PASS,
                    message=f"Matches pattern '{meta.pattern}'.",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                passed_count += 1
            else:
                chk = VerificationCheck(
                    rule_id="RULE-PAT-003",
                    result=VerificationCheckResult.FAIL,
                    message=f"Value '{proposed}' does not match pattern '{meta.pattern}'.",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                failed_count += 1

        # ------------------------------------------------------------------
        # RULE-VOCAB-004: Controlled Vocabulary
        # ------------------------------------------------------------------
        if meta.allowed_values and proposed and str(proposed).strip():
            raw_str = str(proposed).strip()
            if raw_str in meta.allowed_values:
                chk = VerificationCheck(
                    rule_id="RULE-VOCAB-004",
                    result=VerificationCheckResult.PASS,
                    message="Value in controlled vocabulary.",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                passed_count += 1
            else:
                chk = VerificationCheck(
                    rule_id="RULE-VOCAB-004",
                    result=VerificationCheckResult.FAIL,
                    message=f"Value '{proposed}' not in allowed enums: {meta.allowed_values}.",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                failed_count += 1

        # ------------------------------------------------------------------
        # RULE-CONSENT-007: Consent Indicator Check
        # ------------------------------------------------------------------
        if field_name == "consent_indicator" and proposed and str(proposed).strip():
            raw_str = str(proposed).strip().upper()
            if raw_str in ["YES", "NO"]:
                normalized = raw_str
                chk = VerificationCheck(
                    rule_id="RULE-CONSENT-007",
                    result=VerificationCheckResult.PASS,
                    message=f"Consent indicator valid ('{raw_str}').",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                passed_count += 1
            else:
                chk = VerificationCheck(
                    rule_id="RULE-CONSENT-007",
                    result=VerificationCheckResult.FAIL,
                    message=f"Consent indicator '{proposed}' invalid; must be 'YES' or 'NO'.",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                failed_count += 1

        # ------------------------------------------------------------------
        # RULE-SENS-006: Sensitivity Policy Guardrail
        # ------------------------------------------------------------------
        if meta.sensitivity in [SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE] or meta.mandatory_human_review:
            chk = VerificationCheck(
                rule_id="RULE-SENS-006",
                result=VerificationCheckResult.WARNING,
                message=f"Field classified as '{meta.sensitivity.value}' — mandatory human review required.",
                field_name=field_name,
            )
            f_checks.append(chk)
            all_checks.append(chk)
            warning_count += 1

        # ------------------------------------------------------------------
        # RULE-NORM-009: Normalized-Value Validity & Transformation Tracking
        # ------------------------------------------------------------------
        if isinstance(proposed, str):
            trimmed = proposed.strip()
            if normalized != proposed:
                transformations.append({
                    "field_name": field_name,
                    "original_value": proposed,
                    "normalized_value": normalized,
                    "rule_id": "RULE-NORM-009",
                    "change_reason": "Whitespace trimming / ISO formatting",
                })
                chk = VerificationCheck(
                    rule_id="RULE-NORM-009",
                    result=VerificationCheckResult.PASS,
                    message=f"Normalized value from '{proposed}' to '{normalized}'.",
                    field_name=field_name,
                )
                f_checks.append(chk)
                all_checks.append(chk)
                passed_count += 1
            elif trimmed != proposed:
                normalized = trimmed
                transformations.append({
                    "field_name": field_name,
                    "original_value": proposed,
                    "normalized_value": normalized,
                    "rule_id": "RULE-NORM-009",
                    "change_reason": "Whitespace trimming",
                })

        # ------------------------------------------------------------------
        # RULE-EVID-010: Field Evidence Verification Check
        # ------------------------------------------------------------------
        evidence_obj = candidate.get("evidence")
        bbox = None
        if isinstance(evidence_obj, dict):
            bbox = evidence_obj.get("bounding_box")
        elif hasattr(evidence_obj, "bounding_box"):
            bbox = getattr(evidence_obj, "bounding_box")

        if not bbox:
            bbox = candidate.get("bounding_box")

        if bbox and len(bbox) == 4:
            ymin, xmin, ymax, xmax = bbox
            valid_area = (ymax > ymin) and (xmax > xmin)
        else:
            valid_area = False

        if valid_area:
            chk = VerificationCheck(
                rule_id="RULE-EVID-010",
                result=VerificationCheckResult.PASS,
                message=f"Field evidence bounding box {bbox} is valid.",
                field_name=field_name,
            )
            f_checks.append(chk)
            all_checks.append(chk)
            passed_count += 1
        else:
            chk = VerificationCheck(
                rule_id="RULE-EVID-010",
                result=VerificationCheckResult.FAIL,
                message=f"Field evidence bounding box {bbox} is invalid or has zero area.",
                field_name=field_name,
            )
            f_checks.append(chk)
            all_checks.append(chk)
            failed_count += 1

        field_checks_map[field_name] = f_checks
        normalized_map[field_name] = normalized

    # ------------------------------------------------------------------
    # RULE-CROSS-005: Cross-Field Consistency Checks
    # ------------------------------------------------------------------
    if doc_type == DocumentType.FIELD_INSPECTION:
        insp_date_str = extracted_candidates.get("inspection_date", {}).get("proposed_value")
        follow_date_str = extracted_candidates.get("followup_date", {}).get("proposed_value")

        if insp_date_str and follow_date_str:
            try:
                dt_insp = datetime.strptime(str(insp_date_str).strip(), "%Y-%m-%d")
                dt_follow = datetime.strptime(str(follow_date_str).strip(), "%Y-%m-%d")
                if dt_follow < dt_insp:
                    chk = VerificationCheck(
                        rule_id="RULE-CROSS-005",
                        result=VerificationCheckResult.FAIL,
                        message="Follow-up date cannot be earlier than inspection date.",
                        field_name="followup_date",
                    )
                    field_checks_map.setdefault("followup_date", []).append(chk)
                    all_checks.append(chk)
                    failed_count += 1
                else:
                    chk = VerificationCheck(
                        rule_id="RULE-CROSS-005",
                        result=VerificationCheckResult.PASS,
                        message="Follow-up date is after or equal to inspection date.",
                        field_name="followup_date",
                    )
                    field_checks_map.setdefault("followup_date", []).append(chk)
                    all_checks.append(chk)
                    passed_count += 1
            except ValueError:
                pass

    elif doc_type == DocumentType.ATTENDANCE_REGISTER:
        t_in = extracted_candidates.get("time_in", {}).get("proposed_value")
        t_out = extracted_candidates.get("time_out", {}).get("proposed_value")

        if t_in and t_out:
            try:
                dt_in = datetime.strptime(str(t_in).strip(), "%H:%M")
                dt_out = datetime.strptime(str(t_out).strip(), "%H:%M")
                if dt_out < dt_in:
                    chk = VerificationCheck(
                        rule_id="RULE-CROSS-005",
                        result=VerificationCheckResult.FAIL,
                        message="Time out cannot be earlier than time in.",
                        field_name="time_out",
                    )
                    field_checks_map.setdefault("time_out", []).append(chk)
                    all_checks.append(chk)
                    failed_count += 1
                else:
                    chk = VerificationCheck(
                        rule_id="RULE-CROSS-005",
                        result=VerificationCheckResult.PASS,
                        message="Time out is after or equal to time in.",
                        field_name="time_out",
                    )
                    field_checks_map.setdefault("time_out", []).append(chk)
                    all_checks.append(chk)
                    passed_count += 1
            except ValueError:
                pass

    # ------------------------------------------------------------------
    # RULE-MISSING-008: Missing / Conflicting Values Check
    # ------------------------------------------------------------------
    form_comp = extracted_candidates.get("form_completeness", {}).get("proposed_value")
    if form_comp and str(form_comp).strip().upper() == "COMPLETE":
        for fn, meta in meta_dict.items():
            if meta.required:
                val = extracted_candidates.get(fn, {}).get("proposed_value")
                if val is None or str(val).strip() == "":
                    chk = VerificationCheck(
                        rule_id="RULE-MISSING-008",
                        result=VerificationCheckResult.FAIL,
                        message=f"Form marked COMPLETE but required field '{meta.display_name}' is missing.",
                        field_name=fn,
                    )
                    field_checks_map.setdefault(fn, []).append(chk)
                    all_checks.append(chk)
                    failed_count += 1

    # ------------------------------------------------------------------
    # RULE-COMP-011: Cross-Field Consent & Contact Completeness Verification
    # ------------------------------------------------------------------
    if doc_type == DocumentType.CUSTOMER_ONBOARDING:
        consent_val = extracted_candidates.get("consent_indicator", {}).get("proposed_value")
        if consent_val and str(consent_val).strip().upper() == "YES":
            missing_contacts = []
            for fn in ["applicant_name", "contact_number", "email_address"]:
                cand = extracted_candidates.get(fn, {})
                val = cand.get("proposed_value")
                if val is None or str(val).strip() == "" or cand.get("is_absent") or cand.get("is_unreadable"):
                    missing_contacts.append(fn)

            if missing_contacts:
                chk = VerificationCheck(
                    rule_id="RULE-COMP-011",
                    result=VerificationCheckResult.FAIL,
                    message=f"Consent indicator is 'YES' but mandatory contact field(s) {missing_contacts} missing/unreadable.",
                    field_name="consent_indicator",
                )
                field_checks_map.setdefault("consent_indicator", []).append(chk)
                all_checks.append(chk)
                failed_count += 1
            else:
                chk = VerificationCheck(
                    rule_id="RULE-COMP-011",
                    result=VerificationCheckResult.PASS,
                    message="Consent indicator 'YES' matches complete contact PII details.",
                    field_name="consent_indicator",
                )
                field_checks_map.setdefault("consent_indicator", []).append(chk)
                all_checks.append(chk)
                passed_count += 1

    return VerificationResult(
        agent_version=AGENT_VERSION,
        document_type=doc_type,
        checks=all_checks,
        field_checks=field_checks_map,
        normalized_values=normalized_map,
        value_transformations=transformations,
        total_checks_run=len(all_checks),
        passed_checks_count=passed_count,
        failed_checks_count=failed_count,
        warning_checks_count=warning_count,
        verification_metadata={
            "rules_evaluated": [
                "RULE-REQ-001", "RULE-DATE-002", "RULE-PAT-003",
                "RULE-VOCAB-004", "RULE-CROSS-005", "RULE-SENS-006",
                "RULE-CONSENT-007", "RULE-MISSING-008", "RULE-NORM-009"
            ]
        },
    )


def verify_extracted_fields(
    doc_type: DocumentType,
    extracted_candidates: Dict[str, Dict[str, Any]],
) -> Dict[str, Tuple[List[VerificationCheck], str]]:
    """
    Backward-compatible helper function.
    Executes run_deterministic_verification() and returns the legacy
    Dict[field_name, Tuple[checks_list, normalized_value]] format.
    """
    res = run_deterministic_verification(doc_type, extracted_candidates)

    legacy_results: Dict[str, Tuple[List[VerificationCheck], str]] = {}
    for fn, candidate in extracted_candidates.items():
        checks = res.field_checks.get(fn, [])
        normalized = res.normalized_values.get(fn, candidate.get("proposed_value"))
        legacy_results[fn] = (checks, normalized)

    return legacy_results
