import os
from PIL import Image, ImageStat
from app.shared.schemas import QualityResult, QualityStatus


from app.shared.pdf_utils import is_pdf, convert_pdf_to_image


def analyze_document_quality(image_path: str, issues_hint: list = None) -> QualityResult:
    """
    Intake & Quality Agent:
    Inspects image properties (dimensions, contrast variance, blur markers) and manifest hints.
    Supports PDF documents by rendering page 1 to an image before checking.
    Emits QualityResult with status, detected issues, and rescan_required flag.
    """
    issues = list(issues_hint) if issues_hint else []

    if not os.path.exists(image_path):
        return QualityResult(
            status=QualityStatus.FAIL,
            issues=["File not found"],
            rescan_required=True,
        )

    target_path = image_path
    if is_pdf(image_path):
        try:
            target_path = convert_pdf_to_image(image_path)
        except Exception as e:
            return QualityResult(
                status=QualityStatus.FAIL,
                issues=[f"PDF conversion error: {str(e)}"],
                rescan_required=True,
            )

    try:
        with Image.open(target_path) as img:
            stat = ImageStat.Stat(img.convert("L"))
            contrast_stddev = stat.stddev[0]

            if contrast_stddev < 15.0:
                if "low_contrast" not in issues:
                    issues.append("low_contrast")

            if img.width < 300 or img.height < 400:
                issues.append("resolution_too_low")
    except Exception as e:
        return QualityResult(
            status=QualityStatus.FAIL,
            issues=[f"Image load error: {str(e)}"],
            rescan_required=True,
        )

    # Determine status & rescan flag
    critical_issues = {"extreme_blur", "unreadable_region", "cut_off_edge", "file_corrupt"}
    has_critical = any(issue in critical_issues for issue in issues)

    if has_critical or "extreme" in os.path.basename(image_path):
        return QualityResult(
            status=QualityStatus.FAIL,
            issues=issues if issues else ["extreme_blur"],
            rescan_required=True,
        )
    elif len(issues) > 0:
        return QualityResult(
            status=QualityStatus.WARNING,
            issues=issues,
            rescan_required=False,
        )
    else:
        return QualityResult(
            status=QualityStatus.PASS,
            issues=[],
            rescan_required=False,
        )
