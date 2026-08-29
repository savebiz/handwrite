from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    FIELD_INSPECTION = "field_inspection"
    CUSTOMER_ONBOARDING = "customer_onboarding"
    UNKNOWN = "unknown"


class QualityStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class QualityResult(BaseModel):
    status: QualityStatus
    issues: List[str] = Field(default_factory=list)
    rescan_required: bool = False


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
    field_results: List[FieldResult] = Field(default_factory=list)
    record_status: RecordStatusEnum = RecordStatusEnum.PROCESSING
    audit_events: List[AuditEvent] = Field(default_factory=list)
    schema_version: str = "1.0.0"
    agent_version: str = "1.0.0"
