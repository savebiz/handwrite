import os
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

# In-memory / file-backed DB store
DB_DIR = "outputs/db"
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs("data/synthetic", exist_ok=True)
os.makedirs("outputs/crops", exist_ok=True)
os.makedirs("app/static", exist_ok=True)

app.mount("/synthetic", StaticFiles(directory="data/synthetic"), name="synthetic")
app.mount("/crops", StaticFiles(directory="outputs/crops"), name="crops")
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")


def save_record_to_db(record: DocumentRecord):
    path = os.path.join(DB_DIR, f"{record.document_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(record.model_dump_json(indent=2))


def load_record_from_db(doc_id: str) -> Optional[DocumentRecord]:
    path = os.path.join(DB_DIR, f"{doc_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return DocumentRecord.model_validate_json(f.read())


def list_records_from_db() -> List[DocumentRecord]:
    records = []
    if not os.path.exists(DB_DIR):
        return records
    for fname in os.listdir(DB_DIR):
        if fname.endswith(".json"):
            rec = load_record_from_db(fname[:-5])
            if rec:
                records.append(rec)
    return records


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

    if sample_id and os.path.exists("data/manifests/manifest.json"):
        with open("data/manifests/manifest.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)
        sample = next((s for s in manifest["samples"] if s["document_id"] == sample_id), None)
        if sample:
            image_path = sample["image_path"]
            gold_path = sample["gold_label_path"]
            issues_hint = sample.get("issues", [])
            doc_type_hint = sample["document_type"]

    if file:
        os.makedirs("data/synthetic/uploads", exist_ok=True)
        image_path = f"data/synthetic/uploads/{file.filename}"
        with open(image_path, "wb") as f:
            f.write(await file.read())

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


@app.post("/api/evaluation/run")
def run_evaluation_suite():
    results = evaluate_run()
    return results
