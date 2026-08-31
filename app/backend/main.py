from __future__ import annotations
import os
import sys

# Ensure repository root is on sys.path for Vercel Serverless Functions
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import json
import io
import csv
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.shared.schemas import (
    DocumentRecord,
    ReviewerDecisionEnum,
    RecordStatusEnum,
    SensitivityEnum,
    ActorEnum,
    DecisionEnum,
    ExportFormatEnum,
    FieldSelectionPayload,
)
from app.backend.pipeline import process_document_pipeline
from app.backend.audit import log_audit_event
from evaluation.evaluate import evaluate_run

app = FastAPI(title="HandWrite Verify API", version="1.0.0")

# CORS middleware for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import tempfile
from app.backend.db import (
    save_record as save_record_to_db,
    load_record as load_record_from_db,
    list_records as list_records_from_db,
)

# Directory creation with read-only serverless filesystem safety
for d in ["outputs/db", "data/synthetic", "outputs/crops", "app/static"]:
    try:
        os.makedirs(d, exist_ok=True)
    except (OSError, PermissionError):
        pass

synthetic_dir = "data/synthetic" if os.path.exists("data/synthetic") else os.path.join(tempfile.gettempdir(), "data", "synthetic")
crops_dir = "outputs/crops" if os.path.exists("outputs/crops") else os.path.join(tempfile.gettempdir(), "outputs", "crops")
static_dir = "app/static" if os.path.exists("app/static") else os.path.join(tempfile.gettempdir(), "app", "static")

for d in [synthetic_dir, crops_dir, static_dir]:
    try:
        os.makedirs(d, exist_ok=True)
    except (OSError, PermissionError):
        pass

if os.path.exists(synthetic_dir):
    app.mount("/synthetic", StaticFiles(directory=synthetic_dir), name="synthetic")
if os.path.exists(crops_dir):
    app.mount("/crops", StaticFiles(directory=crops_dir), name="crops")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")


class FieldReviewAction(BaseModel):
    field_name: str
    action: ReviewerDecisionEnum  # approved, corrected, rejected
    reviewer_value: Optional[str] = None
    reviewer_reason: Optional[str] = None


class RecordReviewPayload(BaseModel):
    reviewer_id: str = "reviewer-1"
    overall_action: Optional[str] = None  # approved, rescan
    reason: Optional[str] = None
    field_reviews: List[FieldReviewAction] = []


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "HandWrite Verify API", "version": "1.0.0"}


@app.post("/api/documents/upload")
async def upload_document(
    file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    doc_type_hint: Optional[str] = Form(None),
):
    doc_id = sample_id or f"doc-{os.urandom(4).hex()}"
    image_path = f"data/synthetic/upload_{doc_id}.png"
    gold_path = None
    issues_hint = []

    manifest_path = "data/manifests/manifest.json"
    if sample_id and os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            sample = next((s for s in manifest["samples"] if s["document_id"] == sample_id), None)
            if sample:
                image_path = sample["image_path"]
                gold_path = sample["gold_label_path"]
                issues_hint = sample.get("issues", [])
                doc_type_hint = sample["document_type"]
        except (OSError, json.JSONDecodeError):
            pass

    if file:
        upload_dir = "data/synthetic/uploads"
        try:
            os.makedirs(upload_dir, exist_ok=True)
            # Test writability
            test_path = os.path.join(upload_dir, ".write_test")
            with open(test_path, "w") as wf:
                wf.write("ok")
            os.remove(test_path)
        except (OSError, PermissionError):
            upload_dir = os.path.join(tempfile.gettempdir(), "data", "synthetic", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
        image_path = os.path.join(upload_dir, file.filename)
        with open(image_path, "wb") as wf:
            wf.write(await file.read())

    record = process_document_pipeline(
        image_path=image_path,
        document_id=doc_id,
        gold_data_path=gold_path,
        issues_hint=issues_hint,
        doc_type_hint=doc_type_hint,
    )

    save_record_to_db(record)
    return record


@app.get("/api/documents/queue")
def get_document_queue():
    records = list_records_from_db()
    # Sort: rescan_required & awaiting_review first
    priority_order = {
        RecordStatusEnum.RESCAN_REQUIRED: 0,
        RecordStatusEnum.AWAITING_REVIEW: 1,
        RecordStatusEnum.PROCESSING: 2,
        RecordStatusEnum.APPROVED: 3,
        RecordStatusEnum.REJECTED: 4,
    }
    records.sort(key=lambda r: priority_order.get(r.record_status, 99))
    return records


@app.get("/api/documents/{doc_id}")
def get_document_detail(doc_id: str):
    record = load_record_from_db(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document record not found")
    return record


@app.post("/api/documents/{doc_id}/review")
def submit_document_review(doc_id: str, payload: RecordReviewPayload):
    record = load_record_from_db(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document record not found")

    # Handle document-level rescan request
    if payload.overall_action == "rescan":
        rescan_reason = (payload.reason or "").strip()
        if not rescan_reason:
            raise HTTPException(
                status_code=400,
                detail="Document rescan request requires a non-empty reviewer reason.",
            )
        record.record_status = RecordStatusEnum.RESCAN_REQUIRED
        record.document_quality.rescan_required = True

        evt = log_audit_event(
            actor=ActorEnum.REVIEWER,
            action="DOCUMENT_RESCAN_REQUESTED",
            details={
                "document_id": doc_id,
                "reviewer_id": payload.reviewer_id,
                "reason": rescan_reason,
            },
        )
        record.audit_events.append(evt)
        save_record_to_db(record)
        return record

    # Process field-level reviews
    for review in payload.field_reviews:
        field_obj = next((f for f in record.field_results if f.field_name == review.field_name), None)
        if not field_obj:
            continue

        reason_str = (review.reviewer_reason or "").strip()

        # Enforce reason requirement for correction & rejection
        if review.action == ReviewerDecisionEnum.CORRECTED:
            if not reason_str:
                raise HTTPException(
                    status_code=400,
                    detail=f"Field correction for '{review.field_name}' requires a non-empty reviewer reason.",
                )
            if review.reviewer_value is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Field correction for '{review.field_name}' requires a non-null reviewer value.",
                )
            field_obj.reviewer_decision = ReviewerDecisionEnum.CORRECTED
            field_obj.reviewer_value = review.reviewer_value
            field_obj.normalized_value = review.reviewer_value
            field_obj.reviewer_reason = reason_str

        elif review.action == ReviewerDecisionEnum.REJECTED:
            if not reason_str:
                raise HTTPException(
                    status_code=400,
                    detail=f"Field rejection for '{review.field_name}' requires a non-empty reviewer reason.",
                )
            field_obj.reviewer_decision = ReviewerDecisionEnum.REJECTED
            field_obj.reviewer_value = None
            field_obj.reviewer_reason = reason_str

        elif review.action == ReviewerDecisionEnum.APPROVED:
            field_obj.reviewer_decision = ReviewerDecisionEnum.APPROVED
            field_obj.reviewer_value = field_obj.normalized_value or field_obj.proposed_value
            field_obj.reviewer_reason = reason_str or "Approved by human reviewer."

        # Audit event per field review
        field_evt = log_audit_event(
            actor=ActorEnum.REVIEWER,
            action="FIELD_REVIEWED",
            details={
                "document_id": doc_id,
                "field_name": review.field_name,
                "action": review.action.value,
                "reviewer_value": field_obj.reviewer_value,
                "reviewer_reason": field_obj.reviewer_reason,
            },
        )
        record.audit_events.append(field_evt)

    # Resolve overall record status
    all_resolved = all(
        f.reviewer_decision in [ReviewerDecisionEnum.APPROVED, ReviewerDecisionEnum.CORRECTED, ReviewerDecisionEnum.NOT_REQUIRED]
        for f in record.field_results
    )
    all_sensitive_approved = all(
        f.reviewer_decision in [ReviewerDecisionEnum.APPROVED, ReviewerDecisionEnum.CORRECTED]
        for f in record.field_results
        if f.sensitivity in [SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE]
    )

    if any(f.reviewer_decision == ReviewerDecisionEnum.REJECTED for f in record.field_results):
        record.record_status = RecordStatusEnum.REJECTED
    elif all_resolved and all_sensitive_approved:
        record.record_status = RecordStatusEnum.APPROVED
    else:
        record.record_status = RecordStatusEnum.AWAITING_REVIEW

    evt = log_audit_event(
        actor=ActorEnum.REVIEWER,
        action="DOCUMENT_REVIEW_SUBMITTED",
        details={
            "document_id": doc_id,
            "reviewer_id": payload.reviewer_id,
            "fields_reviewed": len(payload.field_reviews),
            "final_record_status": record.record_status.value,
        },
    )
    record.audit_events.append(evt)

    save_record_to_db(record)
    return record


@app.get("/api/documents/{doc_id}/export")
def export_document_record(doc_id: str, format: str = "json"):
    record = load_record_from_db(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document record not found")

    # Guardrail 1: Record status must be APPROVED
    if record.record_status != RecordStatusEnum.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Export blocked: Cannot export record in '{record.record_status.value}' state. Record must be 'approved' by human reviewer first.",
        )

    # Guardrail 2: Sensitive field check — every sensitive field must be explicitly approved/corrected by a human
    for f in record.field_results:
        if f.sensitivity in [SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE]:
            if f.reviewer_decision not in [ReviewerDecisionEnum.APPROVED, ReviewerDecisionEnum.CORRECTED]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Export blocked: Sensitive PII field '{f.field_name}' ({f.sensitivity.value}) requires explicit human reviewer approval before export.",
                )

    export_data = {
        "document_id": record.document_id,
        "document_type": record.document_type.value,
        "record_status": record.record_status.value,
        "schema_version": record.schema_version,
        "agent_version": record.agent_version,
        "verified_fields": {},
    }

    for f in record.field_results:
        final_val = f.reviewer_value if f.reviewer_value is not None else (f.normalized_value or f.proposed_value)
        export_data["verified_fields"][f.field_name] = {
            "display_name": f.display_name,
            "value": final_val,
            "decision": f.decision.value,
            "reviewer_decision": f.reviewer_decision.value,
            "reviewer_reason": f.reviewer_reason,
            "sensitivity": f.sensitivity.value,
        }

    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Field Name", "Display Name", "Verified Value", "Sensitivity", "Reviewer Decision", "Reviewer Reason"])
        for f_name, f_info in export_data["verified_fields"].items():
            writer.writerow([
                f_name,
                f_info["display_name"],
                f_info["value"],
                f_info["sensitivity"],
                f_info["reviewer_decision"],
                f_info.get("reviewer_reason") or "",
            ])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={doc_id}_export.csv"},
        )

    return JSONResponse(content=export_data)


def validate_field_eligibility(f) -> tuple[bool, str]:
    if f.sensitivity in [SensitivityEnum.PERSONAL, SensitivityEnum.SENSITIVE]:
        if f.reviewer_decision not in [ReviewerDecisionEnum.APPROVED, ReviewerDecisionEnum.CORRECTED]:
            return False, f"Sensitive PII field '{f.field_name}' requires explicit human approval before selection."

    val = f.reviewer_value if f.reviewer_value is not None else (f.normalized_value or f.proposed_value)
    if val is None or str(val).strip() == "":
        return False, f"Field '{f.field_name}' has no usable value."

    if f.decision != DecisionEnum.AUTO_ACCEPT and f.reviewer_decision not in [ReviewerDecisionEnum.APPROVED, ReviewerDecisionEnum.CORRECTED]:
        return False, f"Field '{f.field_name}' requires human review or correction."

    return True, "Eligible"


@app.post("/api/documents/{doc_id}/export-selected")
def export_selected_fields(doc_id: str, payload: FieldSelectionPayload):
    record = load_record_from_db(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document record not found")

    if record.record_status != RecordStatusEnum.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Action blocked: Cannot save/export record in '{record.record_status.value}' state. Record must be 'approved' first.",
        )

    if not payload.selected_fields:
        raise HTTPException(
            status_code=400,
            detail="Action blocked: No fields selected for save or export.",
        )

    eligible_fields = []
    for f_name in payload.selected_fields:
        field_obj = next((f for f in record.field_results if f.field_name == f_name), None)
        if not field_obj:
            raise HTTPException(status_code=400, detail=f"Field '{f_name}' not found in record.")

        is_ok, reason = validate_field_eligibility(field_obj)
        if not is_ok:
            raise HTTPException(status_code=400, detail=f"Selection blocked: {reason}")
        eligible_fields.append(field_obj)

    if payload.action_type == "save":
        evt = log_audit_event(
            actor=ActorEnum.REVIEWER,
            action="SELECTED_FIELDS_SAVED",
            details={
                "document_id": doc_id,
                "selected_fields": [f.field_name for f in eligible_fields],
                "preset_name": payload.preset_name,
                "count": len(eligible_fields),
            },
        )
        record.audit_events.append(evt)
        save_record_to_db(record)
        return {
            "status": "success",
            "message": f"{len(eligible_fields)} approved fields saved to record {doc_id}.",
            "selected_fields": [f.field_name for f in eligible_fields],
            "record_id": doc_id,
        }

    evt = log_audit_event(
        actor=ActorEnum.REVIEWER,
        action="SELECTED_FIELDS_EXPORTED",
        details={
            "document_id": doc_id,
            "selected_fields": [f.field_name for f in eligible_fields],
            "format": payload.format.value,
            "preset_name": payload.preset_name,
            "count": len(eligible_fields),
        },
    )
    record.audit_events.append(evt)
    save_record_to_db(record)

    export_data = {
        "document_id": record.document_id,
        "document_type": record.document_type.value,
        "record_status": record.record_status.value,
        "preset_name": payload.preset_name,
        "selected_fields_count": len(eligible_fields),
        "verified_fields": {},
    }

    for f in eligible_fields:
        final_val = f.reviewer_value if f.reviewer_value is not None else (f.normalized_value or f.proposed_value)
        export_data["verified_fields"][f.field_name] = {
            "display_name": f.display_name,
            "value": final_val,
            "decision": f.decision.value,
            "reviewer_decision": f.reviewer_decision.value,
            "reviewer_reason": f.reviewer_reason,
            "sensitivity": f.sensitivity.value,
        }

    if payload.format in [ExportFormatEnum.CSV, ExportFormatEnum.EXCEL_COMPATIBLE_CSV]:
        output = io.StringIO()
        if payload.format == ExportFormatEnum.EXCEL_COMPATIBLE_CSV:
            output.write("\ufeff")  # Write UTF-8 BOM for Excel compatibility
        writer = csv.writer(output)
        writer.writerow(["Field Name", "Display Name", "Verified Value", "Sensitivity", "Reviewer Decision", "Reviewer Reason"])
        for f_name, f_info in export_data["verified_fields"].items():
            writer.writerow([
                f_name,
                f_info["display_name"],
                f_info["value"],
                f_info["sensitivity"],
                f_info["reviewer_decision"],
                f_info.get("reviewer_reason") or "",
            ])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={doc_id}_selected_export.csv"},
        )

    return JSONResponse(content=export_data)


@app.post("/api/evaluation/run")
def run_evaluation_suite():
    results = evaluate_run()
    return results
