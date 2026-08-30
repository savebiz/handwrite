"""
scripts/run_pdf_tests.py — Standalone PDF Test Runner

Validates native PDF document capabilities without requiring pytest.
"""
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from app.shared.pdf_utils import is_pdf, convert_image_to_pdf, convert_pdf_to_image
from app.backend.agents.quality_agent import analyze_document_quality
from app.backend.pipeline import process_document_pipeline
from app.shared.schemas import DocumentRecord, DocumentType, QualityStatus


def run_tests():
    print("--- Running Native PDF Document Processing Tests ---")
    passed = 0
    total = 0

    sample_png = "data/synthetic/field-inspection/field_insp_001.png"
    sample_pdf = "data/synthetic/field-inspection/field_insp_001.pdf"

    assert os.path.exists(sample_png), f"Sample missing: {sample_png}"
    if not os.path.exists(sample_pdf):
        convert_image_to_pdf(sample_png, sample_pdf)
    assert os.path.exists(sample_pdf), f"PDF sample missing: {sample_pdf}"

    # Test 1: PDF Detection
    total += 1
    assert is_pdf(sample_pdf) is True
    assert is_pdf(sample_png) is False
    with open(sample_pdf, "rb") as f:
        assert is_pdf(f.read()) is True
    print("[PASS] Test 1: PDF detection (is_pdf for paths and byte streams)")
    passed += 1

    # Test 2: Image-to-PDF Conversion
    total += 1
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_pdf_path = tmp.name
    try:
        convert_image_to_pdf(sample_png, tmp_pdf_path)
        assert os.path.exists(tmp_pdf_path) and os.path.getsize(tmp_pdf_path) > 0
        assert is_pdf(tmp_pdf_path) is True
        print("[PASS] Test 2: Image-to-PDF conversion (convert_image_to_pdf)")
        passed += 1
    finally:
        if os.path.exists(tmp_pdf_path):
            os.remove(tmp_pdf_path)

    # Test 3: PDF-to-Image Rendering
    total += 1
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_png_path = tmp.name
    try:
        rendered_png = convert_pdf_to_image(sample_pdf, tmp_png_path)
        assert os.path.exists(rendered_png) and os.path.getsize(rendered_png) > 0
        print("[PASS] Test 3: PDF-to-Image rendering (convert_pdf_to_image)")
        passed += 1
    finally:
        if os.path.exists(tmp_png_path):
            os.remove(tmp_png_path)

    # Test 4: Quality Agent PDF support
    total += 1
    q_res = analyze_document_quality(sample_pdf)
    assert q_res.status in (QualityStatus.PASS, QualityStatus.WARNING)
    assert q_res.rescan_required is False
    print("[PASS] Test 4: Quality Agent handles PDF document files cleanly")
    passed += 1

    # Test 5: End-to-End Pipeline PDF execution
    total += 1
    rec = process_document_pipeline(
        image_path=sample_pdf,
        document_id="PDF-CLI-001",
        gold_data_path="data/gold-labels/FI-001_gold.json",
        doc_type_hint="field_inspection",
    )
    assert isinstance(rec, DocumentRecord)
    assert rec.document_id == "PDF-CLI-001"
    assert rec.document_type == DocumentType.FIELD_INSPECTION
    assert len(rec.field_results) == 10
    print("[PASS] Test 5: End-to-end agentic pipeline processes PDF into DocumentRecord")
    passed += 1

    print(f"\n[SUCCESS] ALL PDF PROCESSING TESTS PASSED CLEANLY ({passed}/{total}).")


if __name__ == "__main__":
    run_tests()
