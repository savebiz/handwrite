# Specs: Non-Functional Requirements

- **Performance**: End-to-end processing pipeline under 3.0 seconds per document.
- **Security & Privacy**: Zero storage of real customer PII; strict local file sandboxing.
- **Reliability**: Deterministic rules execute 100% reproducible checks; schema validator rejects all non-compliant inputs.
- **Auditability**: Every decision and edit appends an immutable JSON record to `logs/audit.jsonl`.
