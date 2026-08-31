import uuid
from typing import Dict, Any
from app.shared.schemas import (
    DocumentRecord,
    DocumentType,
    FieldResult,
    Evidence,
    ReviewerDecisionEnum,
    ActorEnum,
    IntakeResult,
)
from app.backend.agents.quality_agent import analyze_document_quality, run_intake_and_quality
from app.backend.agents.classification_agent import classify_document
from app.backend.agents.extraction_agent import extract_field_candidates
from app.backend.agents.verification_agent import verify_extracted_fields
from app.backend.agents.triage_agent import triage_field_and_record, determine_record_status
from app.backend.audit import log_audit_event


from app.shared.pdf_utils import is_pdf, convert_pdf_to_image


def process_document_pipeline(
    image_path: str,
    document_id: str = None,
    gold_data_path: str = None,
    issues_hint: list = None,
    doc_type_hint: str = None,
) -> DocumentRecord:
    """
    Executes the full agentic pipeline:
    1. Intake & Quality Agent (supports PNG/JPG/WEBP and PDF)
    2. Document Classification Agent
    3. Field Extraction Agent
    4. Deterministic Verification Agent
    5. Triage Agent
    6. Record Assembly & Audit Logging
    """
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    doc_id = document_id or f"doc-{uuid.uuid4().hex[:8]}"

    # Stage 1: Enhanced Intake & Quality Agent (handles PDF conversion internally)
    intake_res = run_intake_and_quality(
        file_path=image_path,
        document_id=doc_id,
        run_id=run_id,
        issues_hint=issues_hint,
    )
    quality_res = intake_res.quality

    # Resolve actual image path for downstream agents (PDF -> rendered PNG)
    actual_image_path = image_path
    if is_pdf(image_path):
        actual_image_path = convert_pdf_to_image(image_path, default_dir="data/synthetic/uploads")

    # Stage 2: Document Classification Agent
    doc_type, class_conf, class_reason = classify_document(actual_image_path, hint_type=doc_type_hint)

    if doc_type == DocumentType.UNKNOWN:
        quality_res.issues.append("Uncertain document classification category")

    # Stage 3: Field Extraction Agent
    candidates = extract_field_candidates(
        actual_image_path, doc_type, gold_data_path=gold_data_path, issues=issues_hint
    )

    # Stage 4: Deterministic Verification Agent
    verifications = verify_extracted_fields(doc_type, candidates)

    # Stage 5: Triage Agent
    field_results = []
    field_decisions = []

    for field_name, candidate in candidates.items():
        checks, normalized_val = verifications.get(field_name, ([], candidate["proposed_value"]))
        confidence = candidate["confidence"]
        sensitivity = candidate["sensitivity"]

        decision, decision_reason = triage_field_and_record(
            quality=quality_res,
            confidence=confidence,
            sensitivity=sensitivity,
            checks=checks,
        )

        field_decisions.append(decision)

        # Set initial reviewer decision state based on triage decision
        reviewer_decision = (
            ReviewerDecisionEnum.NOT_REQUIRED
            if decision.value == "auto_accept"
            else ReviewerDecisionEnum.PENDING
        )

        field_results.append(
            FieldResult(
                field_name=field_name,
                display_name=candidate["display_name"],
                proposed_value=candidate["proposed_value"],
                normalized_value=normalized_val,
                confidence=confidence,
                decision=decision,
                sensitivity=sensitivity,
                text_style=candidate.get("text_style", "handwritten"),
                evidence=Evidence(
                    page=1,
                    bounding_box=candidate["bounding_box"],
                    crop_reference=f"/crops/{doc_id}_{field_name}.png",
                ),
                verification_checks=checks,
                decision_reason=decision_reason,
                reviewer_decision=reviewer_decision,
            )
        )

    record_status = determine_record_status(field_decisions, quality_res)

    # Audit Logging
    audit_evt = log_audit_event(
        actor=ActorEnum.AGENT,
        action="DOCUMENT_PIPELINE_PROCESSED",
        details={
            "run_id": run_id,
            "document_id": doc_id,
            "document_type": doc_type.value,
            "quality_status": quality_res.status.value,
            "record_status": record_status.value,
            "total_fields": len(field_results),
            "auto_accepted_fields": sum(1 for d in field_decisions if d.value == "auto_accept"),
            "human_review_fields": sum(1 for d in field_decisions if d.value == "human_review"),
        },
    )

    return DocumentRecord(
        run_id=run_id,
        document_id=doc_id,
        document_type=doc_type,
        document_quality=quality_res,
        intake_result=intake_res,
        field_results=field_results,
        record_status=record_status,
        audit_events=[audit_evt],
        schema_version="1.0.0",
        agent_version="1.0.0",
    )
