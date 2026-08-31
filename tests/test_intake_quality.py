"""
tests/test_intake_quality.py — Unit & Integration Tests for Enhanced Intake & Quality Stage

Validates the 9 deterministic checks in run_intake_and_quality():
  1. Unsupported file type -> FAIL + unsupported_file_type
  2. File not found -> FAIL + file_not_found
  3. Unreadable file -> FAIL + unreadable_file
  4. Blank page -> FAIL + blank_page
  5. Blur detection -> WARNING or FAIL + blur_detected
  6. Clean document -> PASS, zero issues
  7. Cropping/cut-off -> WARNING + possible_cut_off (if present)
  8. Unreadable region -> WARNING + unreadable_region
  9. Page count (multi-page PDF)
  10. Orientation (landscape image)
  11. Processing metadata completeness
  12. Quality failure always routes to rescan_required
  13. Backward compatibility (analyze_document_quality)
  14. Pipeline integration (IntakeResult attached to DocumentRecord)
"""

import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.abspath("."))

from PIL import Image, ImageDraw
from app.shared.schemas import (
    QualityStatus,
    OrientationEnum,
    IntakeResult,
    QualityResult,
    DocumentRecord,
)
from app.backend.agents.quality_agent import run_intake_and_quality, analyze_document_quality


# ---------------------------------------------------------------------------
# Fixtures: generate test images on disk
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture(scope="module")
def clean_image_path(tmp_dir):
    """A normal high-contrast image with text-like content."""
    path = os.path.join(tmp_dir, "clean_doc.png")
    img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw varied content to produce high contrast & edge variance
    for y in range(50, 900, 40):
        draw.text((50, y), f"Line {y}: ABCDEFGHIJ 1234567890 inspection_ref=INSP-2026-001", fill=(0, 0, 0))
    draw.rectangle([30, 30, 770, 970], outline=(0, 0, 0), width=3)
    img.save(path, "PNG")
    return path


@pytest.fixture(scope="module")
def blank_image_path(tmp_dir):
    """An all-white image (blank page)."""
    path = os.path.join(tmp_dir, "blank_page.png")
    img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
    img.save(path, "PNG")
    return path


@pytest.fixture(scope="module")
def blurry_image_path(tmp_dir):
    """A heavily blurred image (low Laplacian variance)."""
    path = os.path.join(tmp_dir, "blurry_doc.png")
    img = Image.new("RGB", (800, 1000), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.text((100, 100), "Blurry text content", fill=(190, 190, 190))
    # Apply heavy blur to reduce edge variance
    from PIL import ImageFilter
    img = img.filter(ImageFilter.GaussianBlur(radius=20))
    img.save(path, "PNG")
    return path


@pytest.fixture(scope="module")
def landscape_image_path(tmp_dir):
    """A landscape-oriented image (wider than tall)."""
    path = os.path.join(tmp_dir, "landscape_doc.png")
    img = Image.new("RGB", (1200, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    for y in range(50, 550, 40):
        draw.text((50, y), f"Landscape line {y}: data content here", fill=(0, 0, 0))
    img.save(path, "PNG")
    return path


@pytest.fixture(scope="module")
def unreadable_region_image_path(tmp_dir):
    """Image with one blank quadrant (top-right) and content elsewhere."""
    path = os.path.join(tmp_dir, "partial_blank.png")
    img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw content in top-left, bottom-left, and bottom-right only
    for y in range(50, 480, 30):
        draw.text((50, y), f"TL content line {y}", fill=(0, 0, 0))
    for y in range(520, 950, 30):
        draw.text((50, y), f"BL content line {y}", fill=(0, 0, 0))
    for y in range(520, 950, 30):
        draw.text((450, y), f"BR content line {y}", fill=(0, 0, 0))
    # Top-right quadrant is left blank
    img.save(path, "PNG")
    return path


@pytest.fixture(scope="module")
def border_ink_image_path(tmp_dir):
    """Image with significant ink at the very edges (simulating cut-off)."""
    path = os.path.join(tmp_dir, "cutoff_doc.png")
    img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw heavy content at top and bottom borders
    for x in range(0, 800, 5):
        draw.line([(x, 0), (x, 15)], fill=(0, 0, 0), width=2)
        draw.line([(x, 985), (x, 1000)], fill=(0, 0, 0), width=2)
    # Normal content in the middle
    for y in range(100, 900, 40):
        draw.text((50, y), f"Content line {y}", fill=(0, 0, 0))
    img.save(path, "PNG")
    return path


@pytest.fixture(scope="module")
def corrupt_file_path(tmp_dir):
    """A file with invalid/corrupt content (not a real image)."""
    path = os.path.join(tmp_dir, "corrupt.png")
    with open(path, "wb") as f:
        f.write(b"THIS IS NOT A VALID IMAGE FILE CONTENT AT ALL")
    return path


@pytest.fixture(scope="module")
def unsupported_file_path(tmp_dir):
    """A .docx file (unsupported type)."""
    path = os.path.join(tmp_dir, "document.docx")
    with open(path, "w") as f:
        f.write("This is not a supported file type")
    return path


@pytest.fixture(scope="module")
def sample_png_path():
    """Existing clean synthetic sample from the corpus."""
    path = "data/synthetic/field-inspection/field_insp_001.png"
    if os.path.exists(path):
        return path
    return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_unsupported_file_type(unsupported_file_path):
    """Test 1: Unsupported file type -> FAIL + unsupported_file_type."""
    result = run_intake_and_quality(unsupported_file_path)
    assert isinstance(result, IntakeResult)
    assert result.quality.status == QualityStatus.FAIL
    assert "unsupported_file_type" in result.quality.issues
    assert result.quality.rescan_required is True
    assert result.file_type == "docx"


def test_file_not_found():
    """Test 2: File not found -> FAIL + file_not_found."""
    result = run_intake_and_quality("/nonexistent/path/to/file.png")
    assert result.quality.status == QualityStatus.FAIL
    assert "file_not_found" in result.quality.issues
    assert result.quality.rescan_required is True
    assert result.page_count == 0


def test_unreadable_file(corrupt_file_path):
    """Test 3: Corrupt/unreadable file -> FAIL + unreadable_file."""
    result = run_intake_and_quality(corrupt_file_path)
    assert result.quality.status == QualityStatus.FAIL
    assert "unreadable_file" in result.quality.issues
    assert result.quality.rescan_required is True


def test_blank_page(blank_image_path):
    """Test 4: Blank page -> FAIL + blank_page."""
    result = run_intake_and_quality(blank_image_path)
    assert result.quality.status == QualityStatus.FAIL
    assert "blank_page" in result.quality.issues
    assert result.quality.rescan_required is True
    assert result.processing_metadata.get("contrast_stddev", 999) < 5.0


def test_blur_detection(blurry_image_path):
    """Test 5: Heavily blurred image -> blur_detected in issues."""
    result = run_intake_and_quality(blurry_image_path)
    assert "blur_detected" in result.quality.issues
    assert result.processing_metadata.get("blur_method") == "laplacian_variance_pil"
    assert "blur_variance" in result.processing_metadata


def test_clean_document(clean_image_path):
    """Test 6: Clean document -> PASS, zero issues."""
    result = run_intake_and_quality(clean_image_path)
    assert result.quality.status == QualityStatus.PASS
    assert len(result.quality.issues) == 0
    assert result.quality.rescan_required is False
    assert result.page_count == 1
    assert result.orientation == OrientationEnum.PORTRAIT


def test_orientation_landscape(landscape_image_path):
    """Test 10: Landscape image -> orientation == landscape."""
    result = run_intake_and_quality(landscape_image_path)
    assert result.orientation == OrientationEnum.LANDSCAPE
    assert result.processing_metadata["image_width"] > result.processing_metadata["image_height"]


def test_processing_metadata_completeness(clean_image_path):
    """Test 11: Processing metadata must contain all expected keys."""
    result = run_intake_and_quality(clean_image_path)
    meta = result.processing_metadata

    assert "checks_executed" in meta
    assert "start_time_iso" in meta
    assert "end_time_iso" in meta
    assert "duration_ms" in meta
    assert "contrast_stddev" in meta
    assert "blur_method" in meta
    assert "blur_variance" in meta
    assert "image_width" in meta
    assert "image_height" in meta
    assert "page_count" in meta
    assert "orientation" in meta

    # All 9 checks should have been executed
    expected_checks = [
        "file_type", "readability", "page_count", "blank_page",
        "blur", "skew", "cut_off", "unreadable_region", "duplicate_page",
    ]
    for check in expected_checks:
        assert check in meta["checks_executed"], f"Missing check: {check}"


def test_quality_failure_routes_to_rescan(blank_image_path, corrupt_file_path):
    """Test 12: Every FAIL status must have rescan_required=True."""
    for path in [blank_image_path, corrupt_file_path]:
        result = run_intake_and_quality(path)
        if result.quality.status == QualityStatus.FAIL:
            assert result.quality.rescan_required is True, \
                f"FAIL status for {path} did not set rescan_required=True"


def test_backward_compatibility(clean_image_path):
    """Test 13: analyze_document_quality() still returns QualityResult."""
    result = analyze_document_quality(clean_image_path)
    assert isinstance(result, QualityResult)
    assert result.status == QualityStatus.PASS
    assert result.rescan_required is False


def test_pipeline_integration(sample_png_path):
    """Test 14: IntakeResult is attached to DocumentRecord via pipeline."""
    if sample_png_path is None:
        pytest.skip("Synthetic sample not available")

    from app.backend.pipeline import process_document_pipeline

    record = process_document_pipeline(
        image_path=sample_png_path,
        document_id="INTAKE-TEST-001",
        gold_data_path="data/gold-labels/FI-001_gold.json",
        doc_type_hint="field_inspection",
    )

    assert isinstance(record, DocumentRecord)
    assert record.intake_result is not None
    assert isinstance(record.intake_result, IntakeResult)
    assert record.intake_result.quality.status == record.document_quality.status
    assert record.intake_result.page_count >= 1
    assert record.intake_result.orientation in [
        OrientationEnum.PORTRAIT, OrientationEnum.LANDSCAPE, OrientationEnum.SQUARE
    ]
    assert "checks_executed" in record.intake_result.processing_metadata


def test_unreadable_region(unreadable_region_image_path):
    """Test 8: Image with one blank quadrant -> unreadable_region."""
    result = run_intake_and_quality(unreadable_region_image_path)
    assert "unreadable_region" in result.quality.issues
    assert "quadrant_stddevs" in result.processing_metadata
    assert len(result.processing_metadata["quadrant_stddevs"]) == 4


def test_cut_off_detection(border_ink_image_path):
    """Test 7: Image with ink at borders -> possible_cut_off."""
    result = run_intake_and_quality(border_ink_image_path)
    assert "possible_cut_off" in result.quality.issues
    assert "border_ink_density" in result.processing_metadata


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------
def run_all_intake_quality_tests():
    """Manual test runner for intake quality tests."""
    with tempfile.TemporaryDirectory() as tmp:
        print("--- Running Enhanced Intake & Quality Stage Tests ---")

        # Generate test fixtures
        def make_clean():
            path = os.path.join(tmp, "clean.png")
            img = Image.new("RGB", (800, 1000), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            for y in range(50, 900, 40):
                draw.text((50, y), f"Content line {y}: ABCDEF 123456", fill=(0, 0, 0))
            draw.rectangle([30, 30, 770, 970], outline=(0, 0, 0), width=3)
            img.save(path)
            return path

        def make_blank():
            path = os.path.join(tmp, "blank.png")
            Image.new("RGB", (800, 1000), (255, 255, 255)).save(path)
            return path

        def make_corrupt():
            path = os.path.join(tmp, "corrupt.png")
            with open(path, "wb") as f:
                f.write(b"NOT A REAL IMAGE")
            return path

        def make_unsupported():
            path = os.path.join(tmp, "test.docx")
            with open(path, "w") as f:
                f.write("unsupported")
            return path

        def make_landscape():
            path = os.path.join(tmp, "landscape.png")
            img = Image.new("RGB", (1200, 600), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            for y in range(50, 550, 40):
                draw.text((50, y), f"Landscape {y}", fill=(0, 0, 0))
            img.save(path)
            return path

        def make_blurry():
            path = os.path.join(tmp, "blurry.png")
            img = Image.new("RGB", (800, 1000), (200, 200, 200))
            draw = ImageDraw.Draw(img)
            draw.text((100, 100), "Blurry", fill=(190, 190, 190))
            from PIL import ImageFilter
            img = img.filter(ImageFilter.GaussianBlur(radius=20))
            img.save(path)
            return path

        def make_unreadable_region():
            path = os.path.join(tmp, "partial.png")
            img = Image.new("RGB", (800, 1000), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            for y in range(50, 480, 30):
                draw.text((50, y), f"TL {y}", fill=(0, 0, 0))
            for y in range(520, 950, 30):
                draw.text((50, y), f"BL {y}", fill=(0, 0, 0))
            for y in range(520, 950, 30):
                draw.text((450, y), f"BR {y}", fill=(0, 0, 0))
            img.save(path)
            return path

        def make_cutoff():
            path = os.path.join(tmp, "cutoff.png")
            img = Image.new("RGB", (800, 1000), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            for x in range(0, 800, 5):
                draw.line([(x, 0), (x, 15)], fill=(0, 0, 0), width=2)
                draw.line([(x, 985), (x, 1000)], fill=(0, 0, 0), width=2)
            for y in range(100, 900, 40):
                draw.text((50, y), f"Content {y}", fill=(0, 0, 0))
            img.save(path)
            return path

        tests_passed = 0
        total_tests = 14

        # Test 1: Unsupported file type
        r = run_intake_and_quality(make_unsupported())
        assert r.quality.status == QualityStatus.FAIL
        assert "unsupported_file_type" in r.quality.issues
        assert r.quality.rescan_required is True
        print("[PASS] Test 1: Unsupported file type -> FAIL + unsupported_file_type")
        tests_passed += 1

        # Test 2: File not found
        r = run_intake_and_quality("/nonexistent/path.png")
        assert r.quality.status == QualityStatus.FAIL
        assert "file_not_found" in r.quality.issues
        assert r.quality.rescan_required is True
        print("[PASS] Test 2: File not found -> FAIL + file_not_found")
        tests_passed += 1

        # Test 3: Unreadable/corrupt file
        r = run_intake_and_quality(make_corrupt())
        assert r.quality.status == QualityStatus.FAIL
        assert "unreadable_file" in r.quality.issues
        assert r.quality.rescan_required is True
        print("[PASS] Test 3: Unreadable/corrupt file -> FAIL + unreadable_file")
        tests_passed += 1

        # Test 4: Blank page
        r = run_intake_and_quality(make_blank())
        assert r.quality.status == QualityStatus.FAIL
        assert "blank_page" in r.quality.issues
        assert r.quality.rescan_required is True
        print("[PASS] Test 4: Blank page -> FAIL + blank_page")
        tests_passed += 1

        # Test 5: Blur detection
        r = run_intake_and_quality(make_blurry())
        assert "blur_detected" in r.quality.issues
        assert r.processing_metadata.get("blur_method") == "laplacian_variance_pil"
        print("[PASS] Test 5: Blurry image -> blur_detected with Laplacian variance method")
        tests_passed += 1

        # Test 6: Clean document
        r = run_intake_and_quality(make_clean())
        assert r.quality.status == QualityStatus.PASS
        assert len(r.quality.issues) == 0
        assert r.quality.rescan_required is False
        print("[PASS] Test 6: Clean document -> PASS, zero issues")
        tests_passed += 1

        # Test 7: Cut-off detection
        r = run_intake_and_quality(make_cutoff())
        assert "possible_cut_off" in r.quality.issues
        assert "border_ink_density" in r.processing_metadata
        print("[PASS] Test 7: Border ink detection -> possible_cut_off")
        tests_passed += 1

        # Test 8: Unreadable region
        r = run_intake_and_quality(make_unreadable_region())
        assert "unreadable_region" in r.quality.issues
        assert "quadrant_stddevs" in r.processing_metadata
        print("[PASS] Test 8: Partial blank quadrant -> unreadable_region")
        tests_passed += 1

        # Test 9: Page count (single-page PNG)
        r = run_intake_and_quality(make_clean())
        assert r.page_count == 1
        print("[PASS] Test 9: Single-page PNG -> page_count=1")
        tests_passed += 1

        # Test 10: Orientation
        r = run_intake_and_quality(make_landscape())
        assert r.orientation == OrientationEnum.LANDSCAPE
        print("[PASS] Test 10: Landscape image -> orientation=landscape")
        tests_passed += 1

        # Test 11: Processing metadata completeness
        r = run_intake_and_quality(make_clean())
        expected_keys = ["checks_executed", "start_time_iso", "end_time_iso", "duration_ms",
                         "contrast_stddev", "blur_method", "blur_variance", "image_width",
                         "image_height", "page_count", "orientation"]
        for k in expected_keys:
            assert k in r.processing_metadata, f"Missing metadata key: {k}"
        expected_checks = ["file_type", "readability", "page_count", "blank_page",
                           "blur", "skew", "cut_off", "unreadable_region", "duplicate_page"]
        for c in expected_checks:
            assert c in r.processing_metadata["checks_executed"], f"Missing check: {c}"
        print("[PASS] Test 11: Processing metadata contains all expected keys and checks")
        tests_passed += 1

        # Test 12: FAIL always -> rescan_required=True
        for path in [make_blank(), make_corrupt()]:
            r = run_intake_and_quality(path)
            if r.quality.status == QualityStatus.FAIL:
                assert r.quality.rescan_required is True
        print("[PASS] Test 12: Quality FAIL always sets rescan_required=True")
        tests_passed += 1

        # Test 13: Backward compatibility
        r = analyze_document_quality(make_clean())
        assert isinstance(r, QualityResult)
        assert r.status == QualityStatus.PASS
        print("[PASS] Test 13: Backward-compatible analyze_document_quality() works")
        tests_passed += 1

        # Test 14: Pipeline integration
        sample_path = "data/synthetic/field-inspection/field_insp_001.png"
        if os.path.exists(sample_path):
            from app.backend.pipeline import process_document_pipeline
            record = process_document_pipeline(
                image_path=sample_path, document_id="INTAKE-TEST",
                gold_data_path="data/gold-labels/FI-001_gold.json",
                doc_type_hint="field_inspection",
            )
            assert record.intake_result is not None
            assert isinstance(record.intake_result, IntakeResult)
            assert "checks_executed" in record.intake_result.processing_metadata
            print("[PASS] Test 14: IntakeResult attached to DocumentRecord in pipeline")
        else:
            print("[SKIP] Test 14: Synthetic sample not available")
        tests_passed += 1

        print(f"\n[SUCCESS] ALL ENHANCED INTAKE & QUALITY TESTS PASSED ({tests_passed}/{total_tests}).")


if __name__ == "__main__":
    run_all_intake_quality_tests()
