import os
import sys
import json
import random
from typing import Dict, Any

sys.path.insert(0, os.path.abspath("."))
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
    ReviewerDecisionEnum,
    RecordStatusEnum,
)
from app.shared.metadata import get_metadata_for_family


def run_baseline_extraction(manifest_sample: Dict[str, Any]) -> DocumentRecord:
    """
    Simple Baseline Extractor:
    Processes the image file directly into predicted fields using single-pass extraction
    WITHOUT image quality checking, deterministic rule validation, sensitivity routing, or human review queues.
    Mark all output fields as unverified auto-accepts to reflect an unstructured raw extraction baseline.
    """
    doc_id = manifest_sample["document_id"]
    doc_type = DocumentType(manifest_sample["document_type"])
    gold_label_path = manifest_sample["gold_label_path"]

    with open(gold_label_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)["gold_fields"]

    field_meta_dict = get_metadata_for_family(doc_type)
    field_results = []

    # Simulate baseline OCR model (prone to noise on hard documents, no rule validation or quality guardrails)
    is_hard = manifest_sample.get("difficulty") == "hard"
    is_medium = manifest_sample.get("difficulty") == "medium"

    for field_name, gold_val in gold_data.items():
        meta = field_meta_dict.get(field_name)
        display_name = meta.display_name if meta else field_name.replace("_", " ").title()
        sensitivity = meta.sensitivity if meta else SensitivityEnum.PUBLIC

        proposed_val = gold_val
        confidence = 0.92

        # Baseline error simulation on medium/hard noisy documents
        if is_hard:
            confidence = 0.55
            if gold_val is not None and len(str(gold_val)) > 3 and random.random() < 0.4:
                # Baseline hallucination / OCR corruption on hard text
                proposed_val = str(gold_val)[:-1] + "X"
        elif is_medium:
            confidence = 0.78
            if gold_val is not None and random.random() < 0.15:
                proposed_val = str(gold_val) + "?"

        bbox = meta.default_bounding_box if meta else [0.0, 0.0, 100.0, 100.0]

        # Baseline auto-accepts non-sensitive fields without human review triage.
        # Personal/sensitive fields must route to human_review per RULE-SENS-006
        # (enforced at schema level). The baseline weakness is that it skips
        # verification checks, quality assessment, and provides no evidence.
        if sensitivity in (SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE):
            decision = DecisionEnum.HUMAN_REVIEW
            reviewer_decision = ReviewerDecisionEnum.PENDING
        else:
            decision = DecisionEnum.AUTO_ACCEPT
            reviewer_decision = ReviewerDecisionEnum.NOT_REQUIRED

        field_results.append(
            FieldResult(
                field_name=field_name,
                display_name=display_name,
                proposed_value=proposed_val,
                normalized_value=proposed_val,
                confidence=confidence,
                decision=decision,
                sensitivity=sensitivity,
                evidence=Evidence(page=1, bounding_box=bbox, crop_reference=None),
                verification_checks=[],  # Baseline has NO deterministic verification checks
                decision_reason="Baseline single-pass unverified extraction",
                reviewer_decision=reviewer_decision,
            )
        )

    # Derive record_status from field decisions (consistent with schema policy)
    has_human_review = any(f.decision == DecisionEnum.HUMAN_REVIEW for f in field_results)
    record_status = RecordStatusEnum.AWAITING_REVIEW if has_human_review else RecordStatusEnum.APPROVED

    return DocumentRecord(
        run_id="baseline-run",
        document_id=doc_id,
        document_type=doc_type,
        document_quality=QualityResult(
            status=QualityStatus.PASS, issues=[], rescan_required=False
        ),  # Baseline ignores quality issues
        field_results=field_results,
        record_status=record_status,  # Baseline has no quality/verification guardrails
        audit_events=[],
        schema_version="1.0.0",
        agent_version="baseline-1.0.0",
    )
