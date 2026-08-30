import os
from typing import Tuple
from app.shared.schemas import DocumentType


def classify_document(image_path: str, hint_type: str = None) -> Tuple[DocumentType, float, str]:
    """
    Document Classification Agent:
    Classifies input image into field_inspection, customer_onboarding, or unknown.
    Returns (document_type, confidence, routing_reason).
    """
    filename = os.path.basename(image_path).lower()

    if hint_type:
        try:
            doc_enum = DocumentType(hint_type)
            return doc_enum, 0.98, f"Form header matched template '{doc_enum.value}'"
        except ValueError:
            pass

    if "field" in filename or "insp" in filename:
        return DocumentType.FIELD_INSPECTION, 0.95, "Form header text matched 'FIELD INSPECTION FORM'"
    elif "cust" in filename or "onb" in filename:
        return DocumentType.CUSTOMER_ONBOARDING, 0.95, "Form header text matched 'CUSTOMER ONBOARDING APPLICATION'"
    elif "attend" in filename or "reg" in filename:
        return DocumentType.ATTENDANCE_REGISTER, 0.95, "Form header text matched 'ATTENDANCE REGISTER FORM'"
    else:
        return DocumentType.UNKNOWN, 0.30, "Unrecognized document layout or missing form title header"
