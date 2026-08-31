"""
app/backend/agents/quality_agent.py — Enhanced Intake & Document-Quality Agent

Performs 9 deterministic checks on input documents using PIL-only operations:
  1. File type validation (whitelist)
  2. File readability (open attempt)
  3. Page count & orientation
  4. Blank page detection (pixel stddev)
  5. Blur detection (Laplacian variance proxy)
  6. Skew detection (row-projection heuristic)
  7. Cropping/cut-off detection (border ink density)
  8. Unreadable region detection (quadrant contrast)
  9. Duplicate-page suspicion (perceptual hash, multi-page PDF)

Returns:
  - QualityResult (backward-compatible)
  - IntakeResult (enhanced, with processing_metadata)
"""

import os
import io
import uuid
import hashlib
import time
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from PIL import Image, ImageStat, ImageFilter
from app.shared.schemas import (
    QualityResult,
    QualityStatus,
    IntakeResult,
    OrientationEnum,
)
from app.shared.pdf_utils import is_pdf, convert_pdf_to_image

# ---------------------------------------------------------------------------
# Configuration thresholds (deterministic, documented)
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}
BLANK_PAGE_STDDEV_THRESHOLD = 5.0
LOW_CONTRAST_STDDEV_THRESHOLD = 15.0
BLUR_VARIANCE_FAIL_THRESHOLD = 25.0
BLUR_VARIANCE_WARN_THRESHOLD = 50.0
MIN_WIDTH = 300
MIN_HEIGHT = 400
BORDER_INK_DENSITY_THRESHOLD = 0.08
QUADRANT_UNREADABLE_THRESHOLD = 8.0

# Laplacian 3x3 kernel for edge detection (PIL ImageFilter.Kernel)
LAPLACIAN_KERNEL = ImageFilter.Kernel(
    size=(3, 3),
    kernel=[0, 1, 0, 1, -4, 1, 0, 1, 0],
    scale=1,
    offset=128,
)


# ---------------------------------------------------------------------------
# Helper: compute average hash for duplicate-page detection
# ---------------------------------------------------------------------------
def _average_hash(img: Image.Image, hash_size: int = 8) -> str:
    """Compute a simple average-hash (aHash) of a PIL Image."""
    resized = img.convert("L").resize((hash_size, hash_size), Image.LANCZOS)
    pixels = list(resized.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if p > avg else "0" for p in pixels)
    return hashlib.md5(bits.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Helper: render a specific PDF page to PIL Image
# ---------------------------------------------------------------------------
def _render_pdf_page(pdf_bytes: bytes, page_index: int) -> Optional[Image.Image]:
    """Render a single PDF page to a PIL Image. Returns None on failure."""
    import pypdf

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        if page_index >= len(reader.pages):
            return None
        page = reader.pages[page_index]

        # Try embedded image first
        if len(page.images) > 0:
            try:
                img_data = page.images[0].data
                return Image.open(io.BytesIO(img_data)).convert("RGB")
            except Exception:
                pass

        # Fallback: render text to canvas
        from PIL import ImageDraw

        text = page.extract_text() or "PDF Page"
        img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((40, 40), f"[ PDF PAGE {page_index + 1} ]", fill=(0, 0, 0))
        y = 80
        for line in text.split("\n")[:30]:
            draw.text((40, y), line[:80], fill=(50, 50, 50))
            y += 25
        return img
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Core: run_intake_and_quality (new enhanced entry point)
# ---------------------------------------------------------------------------
def run_intake_and_quality(
    file_path: str,
    document_id: str = None,
    run_id: str = None,
    issues_hint: list = None,
) -> IntakeResult:
    """
    Enhanced Intake & Document-Quality Agent.
    Runs 9 deterministic checks and returns an IntakeResult with full
    processing metadata. All checks use PIL-only operations.
    """
    start_time = time.time()
    start_iso = datetime.now(timezone.utc).isoformat()

    rid = run_id or f"run-{uuid.uuid4().hex[:8]}"
    did = document_id or f"doc-{uuid.uuid4().hex[:8]}"

    issues: List[str] = list(issues_hint) if issues_hint else []
    metadata = {
        "checks_executed": [],
        "checks_unavailable": [],
        "start_time_iso": start_iso,
    }

    page_count = 1
    orientation = OrientationEnum.UNKNOWN
    file_type = "unknown"
    file_size_bytes = 0
    pdf_bytes: Optional[bytes] = None

    # ------------------------------------------------------------------
    # CHECK 1: File type validation
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("file_type")

    if not os.path.exists(file_path):
        return _fail_result(
            rid, did, ["file_not_found"], metadata, start_time,
            file_type="missing", file_size_bytes=0, page_count=0,
        )

    file_size_bytes = os.path.getsize(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    file_type = ext.lstrip(".") if ext else "unknown"

    if ext not in SUPPORTED_EXTENSIONS:
        issues.append("unsupported_file_type")
        return _fail_result(
            rid, did, issues, metadata, start_time,
            file_type=file_type, file_size_bytes=file_size_bytes, page_count=0,
        )

    # ------------------------------------------------------------------
    # CHECK 2: File readability
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("readability")

    target_path = file_path
    is_pdf_file = is_pdf(file_path)

    if is_pdf_file:
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
            target_path = convert_pdf_to_image(file_path)
        except Exception as e:
            issues.append("unreadable_file")
            metadata["readability_error"] = str(e)
            return _fail_result(
                rid, did, issues, metadata, start_time,
                file_type=file_type, file_size_bytes=file_size_bytes, page_count=0,
            )

    try:
        img = Image.open(target_path).convert("RGB")
    except Exception as e:
        issues.append("unreadable_file")
        metadata["readability_error"] = str(e)
        return _fail_result(
            rid, did, issues, metadata, start_time,
            file_type=file_type, file_size_bytes=file_size_bytes, page_count=0,
        )

    width, height = img.size

    # ------------------------------------------------------------------
    # CHECK 3: Page count & orientation
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("page_count")

    if is_pdf_file and pdf_bytes:
        import pypdf

        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            page_count = len(reader.pages)
        except Exception:
            page_count = 1
    else:
        page_count = 1

    metadata["page_count"] = page_count

    if width > height:
        orientation = OrientationEnum.LANDSCAPE
    elif height > width:
        orientation = OrientationEnum.PORTRAIT
    else:
        orientation = OrientationEnum.SQUARE

    metadata["orientation"] = orientation.value
    metadata["image_width"] = width
    metadata["image_height"] = height

    # Resolution check
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        issues.append("resolution_too_low")

    # ------------------------------------------------------------------
    # CHECK 4: Blank page detection
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("blank_page")

    gray = img.convert("L")
    stat = ImageStat.Stat(gray)
    contrast_stddev = stat.stddev[0]
    metadata["contrast_stddev"] = round(contrast_stddev, 2)

    if contrast_stddev < BLANK_PAGE_STDDEV_THRESHOLD:
        issues.append("blank_page")
    elif contrast_stddev < LOW_CONTRAST_STDDEV_THRESHOLD:
        if "low_contrast" not in issues:
            issues.append("low_contrast")

    # ------------------------------------------------------------------
    # CHECK 5: Blur detection (Laplacian variance proxy)
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("blur")
    metadata["blur_method"] = "laplacian_variance_pil"

    try:
        laplacian = gray.filter(LAPLACIAN_KERNEL)
        lap_stat = ImageStat.Stat(laplacian)
        blur_variance = lap_stat.var[0]
        metadata["blur_variance"] = round(blur_variance, 2)
        metadata["blur_threshold_warn"] = BLUR_VARIANCE_WARN_THRESHOLD
        metadata["blur_threshold_fail"] = BLUR_VARIANCE_FAIL_THRESHOLD

        if blur_variance < BLUR_VARIANCE_FAIL_THRESHOLD:
            issues.append("blur_detected")
            metadata["blur_severity"] = "severe"
        elif blur_variance < BLUR_VARIANCE_WARN_THRESHOLD:
            issues.append("blur_detected")
            metadata["blur_severity"] = "moderate"
    except Exception as e:
        metadata["checks_unavailable"].append("blur")
        metadata["blur_error"] = str(e)

    # ------------------------------------------------------------------
    # CHECK 6: Skew detection (row-projection heuristic)
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("skew")
    metadata["skew_method"] = "row_projection_heuristic"

    try:
        # Binarize: threshold at mean intensity
        mean_val = stat.mean[0]
        binarized = gray.point(lambda p: 0 if p < mean_val * 0.7 else 255)
        bin_pixels = list(binarized.get_flattened_data())

        # Compute per-row ink density (fraction of dark pixels)
        row_densities = []
        for row_idx in range(height):
            row_start = row_idx * width
            row_pixels = bin_pixels[row_start: row_start + width]
            ink_count = sum(1 for p in row_pixels if p == 0)
            row_densities.append(ink_count / width if width > 0 else 0)

        # Only consider rows with some ink (>1% density)
        active_rows = [d for d in row_densities if d > 0.01]
        if len(active_rows) > 10:
            row_mean = sum(active_rows) / len(active_rows)
            row_var = sum((d - row_mean) ** 2 for d in active_rows) / len(active_rows)
            metadata["skew_row_variance"] = round(row_var, 6)

            # Check if ink touches both left and right edges asymmetrically
            left_strip = binarized.crop((0, 0, max(1, int(width * 0.05)), height))
            right_strip = binarized.crop((int(width * 0.95), 0, width, height))
            left_ink = sum(1 for p in left_strip.get_flattened_data() if p == 0) / max(1, left_strip.size[0] * left_strip.size[1])
            right_ink = sum(1 for p in right_strip.get_flattened_data() if p == 0) / max(1, right_strip.size[0] * right_strip.size[1])

            edge_asymmetry = abs(left_ink - right_ink)
            metadata["skew_edge_asymmetry"] = round(edge_asymmetry, 4)

            if row_var > 0.005 and edge_asymmetry > 0.05:
                issues.append("skew_detected")
        else:
            metadata["skew_note"] = "insufficient_ink_rows"
    except Exception as e:
        metadata["checks_unavailable"].append("skew")
        metadata["skew_error"] = str(e)

    # ------------------------------------------------------------------
    # CHECK 7: Cropping/cut-off detection (border ink density)
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("cut_off")

    try:
        margin_x = max(1, int(width * 0.02))
        margin_y = max(1, int(height * 0.02))

        borders = {
            "top": gray.crop((0, 0, width, margin_y)),
            "bottom": gray.crop((0, height - margin_y, width, height)),
            "left": gray.crop((0, 0, margin_x, height)),
            "right": gray.crop((width - margin_x, 0, width, height)),
        }

        border_densities = {}
        for name, strip in borders.items():
            strip_binarized = strip.point(lambda p: 0 if p < mean_val * 0.7 else 255)
            total_pixels = strip.size[0] * strip.size[1]
            ink_pixels = sum(1 for p in strip_binarized.get_flattened_data() if p == 0)
            density = ink_pixels / max(1, total_pixels)
            border_densities[name] = round(density, 4)

        metadata["border_ink_density"] = border_densities

        if any(d > BORDER_INK_DENSITY_THRESHOLD for d in border_densities.values()):
            issues.append("possible_cut_off")
    except Exception as e:
        metadata["checks_unavailable"].append("cut_off")
        metadata["cut_off_error"] = str(e)

    # ------------------------------------------------------------------
    # CHECK 8: Unreadable region detection (quadrant contrast)
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("unreadable_region")

    try:
        mid_x, mid_y = width // 2, height // 2
        quadrants = [
            gray.crop((0, 0, mid_x, mid_y)),           # top-left
            gray.crop((mid_x, 0, width, mid_y)),        # top-right
            gray.crop((0, mid_y, mid_x, height)),       # bottom-left
            gray.crop((mid_x, mid_y, width, height)),    # bottom-right
        ]

        quadrant_stddevs = []
        for q in quadrants:
            q_stat = ImageStat.Stat(q)
            quadrant_stddevs.append(round(q_stat.stddev[0], 2))

        metadata["quadrant_stddevs"] = quadrant_stddevs

        normal_quadrants = [s for s in quadrant_stddevs if s >= QUADRANT_UNREADABLE_THRESHOLD]
        low_quadrants = [s for s in quadrant_stddevs if s < QUADRANT_UNREADABLE_THRESHOLD]

        if low_quadrants and normal_quadrants:
            issues.append("unreadable_region")
    except Exception as e:
        metadata["checks_unavailable"].append("unreadable_region")
        metadata["unreadable_region_error"] = str(e)

    # ------------------------------------------------------------------
    # CHECK 9: Duplicate-page suspicion (multi-page PDF only)
    # ------------------------------------------------------------------
    metadata["checks_executed"].append("duplicate_page")

    if is_pdf_file and pdf_bytes and page_count >= 2:
        try:
            page_hashes = []
            for pg_idx in range(min(page_count, 20)):  # cap at 20 pages
                pg_img = _render_pdf_page(pdf_bytes, pg_idx)
                if pg_img:
                    page_hashes.append(_average_hash(pg_img))
                else:
                    page_hashes.append(None)

            metadata["page_hashes"] = page_hashes
            unique_hashes = set(h for h in page_hashes if h is not None)
            non_none_count = sum(1 for h in page_hashes if h is not None)

            if non_none_count > len(unique_hashes):
                issues.append("duplicate_page_suspicion")
        except Exception as e:
            metadata["checks_unavailable"].append("duplicate_page")
            metadata["duplicate_page_error"] = str(e)
    else:
        metadata["duplicate_page_note"] = "not_applicable_single_page"

    # Close image
    img.close()

    # ------------------------------------------------------------------
    # Determine final quality status
    # ------------------------------------------------------------------
    critical_issues = {
        "file_not_found", "unsupported_file_type", "unreadable_file",
        "blank_page", "extreme_blur", "file_corrupt",
    }

    # Also treat hint-based critical issues
    hint_critical = {"extreme_blur", "unreadable_region", "cut_off_edge", "file_corrupt"}
    all_critical = critical_issues | hint_critical

    has_critical = any(issue in all_critical for issue in issues)

    # Severe blur is critical
    if "blur_detected" in issues and metadata.get("blur_severity") == "severe":
        has_critical = True

    if has_critical:
        status = QualityStatus.FAIL
        rescan_required = True
    elif len(issues) > 0:
        status = QualityStatus.WARNING
        rescan_required = False
    else:
        status = QualityStatus.PASS
        rescan_required = False

    # Finalize metadata
    end_time = time.time()
    metadata["end_time_iso"] = datetime.now(timezone.utc).isoformat()
    metadata["duration_ms"] = round((end_time - start_time) * 1000, 2)

    quality = QualityResult(
        status=status,
        issues=issues,
        rescan_required=rescan_required,
    )

    return IntakeResult(
        run_id=rid,
        document_id=did,
        page_count=page_count,
        orientation=orientation,
        quality=quality,
        file_type=file_type,
        file_size_bytes=file_size_bytes,
        processing_metadata=metadata,
    )


# ---------------------------------------------------------------------------
# Backward-compatible entry point (preserves existing API)
# ---------------------------------------------------------------------------
def analyze_document_quality(image_path: str, issues_hint: list = None) -> QualityResult:
    """
    Backward-compatible Intake & Quality Agent entry point.
    Delegates to run_intake_and_quality() and returns only the QualityResult.
    """
    intake = run_intake_and_quality(
        file_path=image_path,
        issues_hint=issues_hint,
    )
    return intake.quality


# ---------------------------------------------------------------------------
# Helper: construct a FAIL IntakeResult quickly
# ---------------------------------------------------------------------------
def _fail_result(
    run_id: str,
    document_id: str,
    issues: List[str],
    metadata: dict,
    start_time: float,
    file_type: str = "unknown",
    file_size_bytes: int = 0,
    page_count: int = 0,
) -> IntakeResult:
    """Construct an IntakeResult with FAIL status and rescan_required=True."""
    end_time = time.time()
    metadata["end_time_iso"] = datetime.now(timezone.utc).isoformat()
    metadata["duration_ms"] = round((end_time - start_time) * 1000, 2)

    return IntakeResult(
        run_id=run_id,
        document_id=document_id,
        page_count=page_count,
        orientation=OrientationEnum.UNKNOWN,
        quality=QualityResult(
            status=QualityStatus.FAIL,
            issues=issues,
            rescan_required=True,
        ),
        file_type=file_type,
        file_size_bytes=file_size_bytes,
        processing_metadata=metadata,
    )
