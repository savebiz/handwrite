# Specs: Shared Data Contract

This specification defines the JSON schema for document records, field results, validation checks, evidence references, and audit logs.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DocumentRecord",
  "type": "object",
  "properties": {
    "run_id": { "type": "string" },
    "document_id": { "type": "string" },
    "document_type": {
      "type": "string",
      "enum": ["field_inspection", "customer_onboarding", "unknown"]
    },
    "document_quality": {
      "type": "object",
      "properties": {
        "status": { "type": "string", "enum": ["pass", "warning", "fail"] },
        "issues": { "type": "array", "items": { "type": "string" } },
        "rescan_required": { "type": "boolean" }
      },
      "required": ["status", "issues", "rescan_required"]
    },
    "field_results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "field_name": { "type": "string" },
          "display_name": { "type": "string" },
          "proposed_value": { "type": ["string", "null"] },
          "normalized_value": { "type": ["string", "null"] },
          "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "decision": {
            "type": "string",
            "enum": ["auto_accept", "human_review", "rescan_required"]
          },
          "sensitivity": {
            "type": "string",
            "enum": ["public", "internal", "personal", "sensitive"]
          },
          "text_style": {
            "type": "string",
            "enum": ["handwritten", "typewritten", "mixed"],
            "default": "handwritten"
          },
          "evidence": {
            "type": "object",
            "properties": {
              "page": { "type": "number" },
              "bounding_box": {
                "type": "array",
                "items": { "type": "number" },
                "minItems": 4,
                "maxItems": 4
              },
              "crop_reference": { "type": ["string", "null"] }
            },
            "required": ["page", "bounding_box"]
          },
          "verification_checks": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "rule_id": { "type": "string" },
                "result": {
                  "type": "string",
                  "enum": ["pass", "fail", "warning", "not_applicable"]
                },
                "message": { "type": "string" }
              },
              "required": ["rule_id", "result", "message"]
            }
          },
          "decision_reason": { "type": "string" },
          "reviewer_value": { "type": ["string", "null"] },
          "reviewer_decision": {
            "type": "string",
            "enum": ["approved", "corrected", "rejected", "pending", "not_required"]
          },
          "reviewer_reason": { "type": ["string", "null"] }
        },
        "required": [
          "field_name",
          "display_name",
          "proposed_value",
          "normalized_value",
          "confidence",
          "decision",
          "sensitivity",
          "evidence",
          "verification_checks",
          "decision_reason",
          "reviewer_decision"
        ]
      }
    },
    "record_status": {
      "type": "string",
      "enum": [
        "processing",
        "awaiting_review",
        "rescan_required",
        "approved",
        "rejected"
      ]
    },
    "audit_events": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "timestamp": { "type": "string" },
          "actor": { "type": "string", "enum": ["agent", "reviewer", "system"] },
          "action": { "type": "string" },
          "details": { "type": "object" }
        },
        "required": ["timestamp", "actor", "action", "details"]
      }
    },
    "schema_version": { "type": "string" },
    "agent_version": { "type": "string" }
  },
  "required": [
    "run_id",
    "document_id",
    "document_type",
    "document_quality",
    "field_results",
    "record_status",
    "audit_events",
    "schema_version",
    "agent_version"
  ]
}
```
