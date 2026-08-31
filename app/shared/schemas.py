from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator


class DocumentType(str, Enum):
    FIELD_INSPECTION = "field_inspection"
    CUSTOMER_ONBOARDING = "customer_onboarding"
    ATTENDANCE_REGISTER = "attendance_register"
    UNKNOWN = "unknown"


class QualityStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class QualityResult(BaseModel):
    status: QualityStatus
    issues: List[str] = Field(default_factory=list)
    rescan_required: bool = False


class OrientationEnum(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE = "square"
    UNKNOWN = "unknown"


class IntakeResult(BaseModel):
    run_id: str
    document_id: str
    page_count: int = 1
    orientation: OrientationEnum = OrientationEnum.UNKNOWN
    quality: QualityResult
    file_type: str = "unknown"
    file_size_bytes: int = 0
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionEnum(str, Enum):
    AUTO_ACCEPT = "auto_accept"
    HUMAN_REVIEW = "human_review"
    RESCAN_REQUIRED = "rescan_required"


class SensitivityEnum(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"


class VerificationCheckResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"


class VerificationCheck(BaseModel):
    rule_id: str
    result: VerificationCheckResult
    message: str
    field_name: Optional[str] = None


class VerificationResult(BaseModel):
    agent_version: str = "1.3.0-verification"
    document_type: DocumentType
    checks: List[VerificationCheck] = Field(default_factory=list)
    field_checks: Dict[str, List[VerificationCheck]] = Field(default_factory=dict)
    normalized_values: Dict[str, Optional[str]] = Field(default_factory=dict)
    value_transformations: List[Dict[str, Any]] = Field(default_factory=list)
    total_checks_run: int = 0
    passed_checks_count: int = 0
    failed_checks_count: int = 0
    warning_checks_count: int = 0
    verification_metadata: Dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    page: int = 1
    bounding_box: List[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Bounding box coordinates [ymin, xmin, ymax, xmax]",
    )
    crop_reference: Optional[str] = None


class ReviewerDecisionEnum(str, Enum):
    APPROVED = "approved"
    CORRECTED = "corrected"
    REJECTED = "rejected"
    PENDING = "pending"
    NOT_REQUIRED = "not_required"


class TextStyleEnum(str, Enum):
    HANDWRITTEN = "handwritten"
    TYPEWRITTEN = "typewritten"
    MIXED = "mixed"


class FieldCandidate(BaseModel):
    field_name: str
    display_name: str
    proposed_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    text_style: TextStyleEnum = TextStyleEnum.HANDWRITTEN
    evidence: Evidence
    sensitivity: SensitivityEnum
    mandatory_human_review: bool = False
    is_unreadable: bool = False
    is_absent: bool = False


class ExtractionResult(BaseModel):
    agent_version: str = "1.2.0-extraction"
    prompt_version_id: str = "prompt-schema-guided-v1.0"
    adapter_type: str = "synthetic_test_adapter"
    document_type: DocumentType
    fields: List[FieldCandidate] = Field(default_factory=list)
    total_expected_fields: int = 0
    extracted_fields_count: int = 0
    unreadable_fields_count: int = 0
    absent_fields_count: int = 0
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)


class FieldResult(BaseModel):
    field_name: str
    display_name: str
    proposed_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    decision: DecisionEnum
    sensitivity: SensitivityEnum
    text_style: TextStyleEnum = TextStyleEnum.HANDWRITTEN
    evidence: Evidence
    verification_checks: List[VerificationCheck] = Field(default_factory=list)
    decision_reason: str
    reviewer_value: Optional[str] = None
    reviewer_decision: ReviewerDecisionEnum = ReviewerDecisionEnum.PENDING
    reviewer_reason: Optional[str] = None

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    @model_validator(mode="after")
    def validate_sensitivity_decision(self) -> "FieldResult":
        """RULE-SENS-006: personal/sensitive fields MUST NOT be auto_accept."""
        if self.decision == DecisionEnum.AUTO_ACCEPT and self.sensitivity in (
            SensitivityEnum.PERSONAL,
            SensitivityEnum.SENSITIVE,
        ):
            raise ValueError(
                f"Policy violation RULE-SENS-006: field with sensitivity "
                f"'{self.sensitivity.value}' cannot have decision 'auto_accept'. "
                f"Must be 'human_review' or 'rescan_required'."
            )
        return self


class RecordStatusEnum(str, Enum):
    PROCESSING = "processing"
    AWAITING_REVIEW = "awaiting_review"
    RESCAN_REQUIRED = "rescan_required"
    APPROVED = "approved"
    REJECTED = "rejected"


class ActorEnum(str, Enum):
    AGENT = "agent"
    REVIEWER = "reviewer"
    SYSTEM = "system"


class AuditEvent(BaseModel):
    timestamp: str  # ISO-8601 string
    actor: ActorEnum
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)


class DocumentRecord(BaseModel):
    run_id: str
    document_id: str
    document_type: DocumentType
    document_quality: QualityResult
    intake_result: Optional[IntakeResult] = None
    extraction_result: Optional[ExtractionResult] = None
    verification_result: Optional[VerificationResult] = None
    field_results: List[FieldResult] = Field(default_factory=list)
    record_status: RecordStatusEnum = RecordStatusEnum.PROCESSING
    audit_events: List[AuditEvent] = Field(default_factory=list)
    schema_version: str = "1.0.0"
    agent_version: str = "1.0.0"

