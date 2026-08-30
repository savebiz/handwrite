"""
tests/test_pdf.py — Unit & Integration Tests for Native PDF Processing

Validates native PDF document capabilities:
  1. PDF detection (is_pdf for file paths and byte streams).
  2. Image-to-PDF conversion (convert_image_to_pdf).
  3. PDF-to-Image rendering (convert_pdf_to_image).
  4. Quality Agent PDF handling (analyze_document_quality on .pdf files).
  5. Agentic Pipeline PDF handling (process_document_pipeline on .pdf files).
  6. FastAPI Upload endpoint PDF handling (POST /api/documents/upload with .pdf file).
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))
from app.shared.pdf_utils import is_pdf, convert_image_to_pdf, convert_pdf_to_image
from app.backend.agents.quality_agent import analyze_document_quality
from app.backend.pipeline import process_document_pipeline
from app.shared.schemas import DocumentRecord, DocumentType, QualityStatus, RecordStatusEnum
from app.backend.main import app


@pytest.fixture(scope="module")
def sample_png_path():
    path = "data/synthetic/field-inspection/field_insp_001.png"
    assert os.path.exists(path), f"PNG sample missing at {path}"
    return path


@pytest.fixture(scope="module")
def sample_pdf_path(sample_png_path):
    pdf_path = "data/synthetic/field-inspection/field_insp_001.pdf"
    if not os.path.exists(pdf_path):
        convert_image_to_pdf(sample_png_path, pdf_path)
    assert os.path.exists(pdf_path)
    return pdf_path


def test_is_pdf_detection(sample_png_path, sample_pdf_path):
    """is_pdf must return True for .pdf paths/bytes and False for PNG files."""
    assert is_pdf(sample_pdf_path) is True
    assert is_pdf(sample_png_path) is False

    with open(sample_pdf_path, "rb") as f:
        pdf_bytes = f.read()
    assert is_pdf(pdf_bytes) is True

    with open(sample_png_path, "rb") as f:
        png_bytes = f.read()
    assert is_pdf(png_bytes) is False


def test_convert_pdf_to_image(sample_pdf_path, tmp_path):
    """convert_pdf_to_image must render PDF Page 1 into a valid PNG image."""
    output_png = str(tmp_path / "rendered_test.png")
    result_path = convert_pdf_to_image(sample_pdf_path, output_png)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_quality_agent_pdf_support(sample_pdf_path):
    """analyze_document_quality must process PDF files without throwing image errors."""
    res = analyze_document_quality(sample_pdf_path)
    assert res.status in (QualityStatus.PASS, QualityStatus.WARNING)
    assert res.rescan_required is False


def test_pipeline_pdf_end_to_end(sample_pdf_path):
    """process_document_pipeline must process a PDF file into a valid DocumentRecord."""
    record = process_document_pipeline(
        image_path=sample_pdf_path,
        document_id="PDF-TEST-001",
        gold_data_path="data/gold-labels/FI-001_gold.json",
        doc_type_hint="field_inspection",
    )

    assert isinstance(record, DocumentRecord)
    assert record.document_id == "PDF-TEST-001"
    assert record.document_type == DocumentType.FIELD_INSPECTION
    assert len(record.field_results) == 10
    assert record.document_quality.status == QualityStatus.PASS


def test_api_upload_pdf_file(sample_pdf_path):
    """POST /api/documents/upload with a .pdf UploadFile must succeed with status 200."""
    client = TestClient(app)
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/api/documents/upload",
            files={"file": ("uploaded_form.pdf", f, "application/pdf")},
            data={"doc_type_hint": "field_inspection"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["document_type"] == "field_inspection"
    assert len(data["field_results"]) == 10
