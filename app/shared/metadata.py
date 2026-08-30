from typing import Dict, List, Optional
from pydantic import BaseModel
from app.shared.schemas import SensitivityEnum, DocumentType


class FieldMetadata(BaseModel):
    field_name: str
    display_name: str
    required: bool
    sensitivity: SensitivityEnum
    data_type: str  # "string", "date", "enum", "phone", "email"
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    default_bounding_box: List[float] = [0.0, 0.0, 100.0, 100.0]
    mandatory_human_review: bool = False


FIELD_INSPECTION_METADATA: Dict[str, FieldMetadata] = {
    "inspection_ref": FieldMetadata(
        field_name="inspection_ref",
        display_name="Inspection Reference",
        required=True,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="string",
        pattern=r"^INSP-\d{4}-\d{3}$",
        default_bounding_box=[100.0, 50.0, 150.0, 400.0],
    ),
    "inspection_date": FieldMetadata(
        field_name="inspection_date",
        display_name="Inspection Date",
        required=True,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="date",
        default_bounding_box=[100.0, 450.0, 150.0, 750.0],
    ),
    "site_location": FieldMetadata(
        field_name="site_location",
        display_name="Site / Location",
        required=True,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="string",
        default_bounding_box=[180.0, 50.0, 230.0, 750.0],
    ),
    "inspector_name": FieldMetadata(
        field_name="inspector_name",
        display_name="Inspector Name",
        required=True,
        sensitivity=SensitivityEnum.PERSONAL,
        data_type="string",
        default_bounding_box=[260.0, 50.0, 310.0, 750.0],
        mandatory_human_review=True,
    ),
    "asset_ref": FieldMetadata(
        field_name="asset_ref",
        display_name="Asset Reference",
        required=True,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="string",
        pattern=r"^AST-\d{5}$",
        default_bounding_box=[340.0, 50.0, 390.0, 400.0],
    ),
    "inspection_status": FieldMetadata(
        field_name="inspection_status",
        display_name="Inspection Status",
        required=True,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="enum",
        allowed_values=["PASS", "FAIL", "NEEDS_ATTENTION"],
        default_bounding_box=[340.0, 450.0, 390.0, 750.0],
    ),
    "observation_finding": FieldMetadata(
        field_name="observation_finding",
        display_name="Observation / Finding",
        required=False,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="string",
        default_bounding_box=[420.0, 50.0, 520.0, 750.0],
    ),
    "action_required": FieldMetadata(
        field_name="action_required",
        display_name="Action Required",
        required=False,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="string",
        default_bounding_box=[550.0, 50.0, 650.0, 750.0],
    ),
    "followup_date": FieldMetadata(
        field_name="followup_date",
        display_name="Follow-up Date",
        required=False,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="date",
        default_bounding_box=[680.0, 50.0, 730.0, 380.0],
    ),
    "form_completeness": FieldMetadata(
        field_name="form_completeness",
        display_name="Form Completeness",
        required=True,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="enum",
        allowed_values=["COMPLETE", "INCOMPLETE"],
        default_bounding_box=[680.0, 420.0, 730.0, 750.0],
    ),
}

CUSTOMER_ONBOARDING_METADATA: Dict[str, FieldMetadata] = {
    "onboarding_ref": FieldMetadata(
        field_name="onboarding_ref",
        display_name="Onboarding Reference",
        required=True,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="string",
        pattern=r"^ONB-\d{4}-\d{3}$",
        default_bounding_box=[100.0, 50.0, 150.0, 400.0],
    ),
    "application_date": FieldMetadata(
        field_name="application_date",
        display_name="Application Date",
        required=True,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="date",
        default_bounding_box=[100.0, 450.0, 150.0, 750.0],
    ),
    "applicant_name": FieldMetadata(
        field_name="applicant_name",
        display_name="Applicant Name",
        required=True,
        sensitivity=SensitivityEnum.PERSONAL,
        data_type="string",
        default_bounding_box=[180.0, 50.0, 230.0, 750.0],
        mandatory_human_review=True,
    ),
    "contact_number": FieldMetadata(
        field_name="contact_number",
        display_name="Contact Number",
        required=True,
        sensitivity=SensitivityEnum.PERSONAL,
        data_type="phone",
        pattern=r"^\+?[0-9]{10,14}$",
        default_bounding_box=[260.0, 50.0, 310.0, 380.0],
        mandatory_human_review=True,
    ),
    "email_address": FieldMetadata(
        field_name="email_address",
        display_name="Email Address",
        required=False,
        sensitivity=SensitivityEnum.PERSONAL,
        data_type="email",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        default_bounding_box=[260.0, 400.0, 310.0, 750.0],
        mandatory_human_review=True,
    ),
    "address_location": FieldMetadata(
        field_name="address_location",
        display_name="Address / Location",
        required=True,
        sensitivity=SensitivityEnum.PERSONAL,
        data_type="string",
        default_bounding_box=[340.0, 50.0, 410.0, 750.0],
        mandatory_human_review=True,
    ),
    "product_requested": FieldMetadata(
        field_name="product_requested",
        display_name="Product Requested",
        required=True,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="enum",
        allowed_values=["Standard", "Premium", "Enterprise"],
        default_bounding_box=[430.0, 50.0, 480.0, 380.0],
    ),
    "id_ref_placeholder": FieldMetadata(
        field_name="id_ref_placeholder",
        display_name="Identity Reference Placeholder",
        required=True,
        sensitivity=SensitivityEnum.SENSITIVE,
        data_type="string",
        pattern=r"^ID-[\*\w]{5,10}$",
        default_bounding_box=[430.0, 400.0, 480.0, 750.0],
        mandatory_human_review=True,
    ),
    "consent_indicator": FieldMetadata(
        field_name="consent_indicator",
        display_name="Consent Indicator",
        required=True,
        sensitivity=SensitivityEnum.PERSONAL,
        data_type="enum",
        allowed_values=["YES", "NO"],
        default_bounding_box=[510.0, 50.0, 560.0, 380.0],
        mandatory_human_review=True,
    ),
    "reviewer_status": FieldMetadata(
        field_name="reviewer_status",
        display_name="Reviewer Status",
        required=True,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="enum",
        allowed_values=["PENDING", "VERIFIED", "REJECTED"],
        default_bounding_box=[510.0, 400.0, 560.0, 750.0],
    ),
    "form_completeness": FieldMetadata(
        field_name="form_completeness",
        display_name="Form Completeness",
        required=True,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="enum",
        allowed_values=["COMPLETE", "INCOMPLETE"],
        default_bounding_box=[590.0, 50.0, 640.0, 750.0],
    ),
}


ATTENDANCE_REGISTER_METADATA: Dict[str, FieldMetadata] = {
    "register_ref": FieldMetadata(
        field_name="register_ref",
        display_name="Register Reference",
        required=True,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="string",
        pattern=r"^ATT-\d{4}-\d{3}$",
        default_bounding_box=[100.0, 50.0, 150.0, 400.0],
    ),
    "record_date": FieldMetadata(
        field_name="record_date",
        display_name="Record Date",
        required=True,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="date",
        default_bounding_box=[100.0, 450.0, 150.0, 750.0],
    ),
    "site_department": FieldMetadata(
        field_name="site_department",
        display_name="Site / Department",
        required=True,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="string",
        default_bounding_box=[180.0, 50.0, 230.0, 750.0],
    ),
    "attendee_name": FieldMetadata(
        field_name="attendee_name",
        display_name="Attendee Name",
        required=True,
        sensitivity=SensitivityEnum.PERSONAL,
        data_type="string",
        default_bounding_box=[260.0, 50.0, 310.0, 750.0],
        mandatory_human_review=True,
    ),
    "staff_ref": FieldMetadata(
        field_name="staff_ref",
        display_name="Staff Reference",
        required=True,
        sensitivity=SensitivityEnum.SENSITIVE,
        data_type="string",
        pattern=r"^EMP-\d{5}$",
        default_bounding_box=[340.0, 50.0, 390.0, 400.0],
        mandatory_human_review=True,
    ),
    "attendance_status": FieldMetadata(
        field_name="attendance_status",
        display_name="Attendance Status",
        required=True,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="enum",
        allowed_values=["PRESENT", "ABSENT", "LATE", "LEAVE"],
        default_bounding_box=[340.0, 450.0, 390.0, 750.0],
    ),
    "time_in": FieldMetadata(
        field_name="time_in",
        display_name="Time In",
        required=False,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="string",
        pattern=r"^[0-2][0-9]:[0-5][0-9]$",
        default_bounding_box=[420.0, 50.0, 470.0, 380.0],
    ),
    "time_out": FieldMetadata(
        field_name="time_out",
        display_name="Time Out",
        required=False,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="string",
        pattern=r"^[0-2][0-9]:[0-5][0-9]$",
        default_bounding_box=[420.0, 400.0, 470.0, 750.0],
    ),
    "supervisor_notes": FieldMetadata(
        field_name="supervisor_notes",
        display_name="Supervisor Notes",
        required=False,
        sensitivity=SensitivityEnum.PUBLIC,
        data_type="string",
        default_bounding_box=[500.0, 50.0, 600.0, 750.0],
    ),
    "form_completeness": FieldMetadata(
        field_name="form_completeness",
        display_name="Form Completeness",
        required=True,
        sensitivity=SensitivityEnum.INTERNAL,
        data_type="enum",
        allowed_values=["COMPLETE", "INCOMPLETE"],
        default_bounding_box=[630.0, 50.0, 680.0, 750.0],
    ),
}


def get_metadata_for_family(doc_type: DocumentType) -> Dict[str, FieldMetadata]:
    if doc_type == DocumentType.FIELD_INSPECTION:
        return FIELD_INSPECTION_METADATA
    elif doc_type == DocumentType.CUSTOMER_ONBOARDING:
        return CUSTOMER_ONBOARDING_METADATA
    elif doc_type == DocumentType.ATTENDANCE_REGISTER:
        return ATTENDANCE_REGISTER_METADATA
    return {}
