# Reusable Skill: Privacy and Security

- **Purpose**: Audit codebase for secret/credential leaks, PII exposure, unapproved sensitive field exports, and immutable audit logging.
- **Human Approval Boundary**: Security review rules and PII export guardrails must be approved by Victor Sabo.
- **Input Files**: `app/backend/main.py`, `app/backend/audit.py`, `.env.example`, `.gitignore`
- **Output Files**: `app/backend/audit.py`, `docs/agent-use-disclosure.md`, `docs/submission-integrity.md`
- **Permitted Actions**: Security auditing, export safety check verification, append-only log format validation.
- **Prohibited Actions**: Allowing un-reviewed PII export or committing secrets.
- **Tests & Evidence Required**: `python tests/test_api.py` (Export Guardrail Test PASS).
- **Escalation Conditions**: Secret key leak, real customer PII in codebase, unauthenticated export route.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Process synthetic anonymized form data only.
2. Zero handwriting hallucination.
3. Verify visual evidence links for all sensitive fields.
4. Separate security auditing from core pipeline processing.
5. Apply deterministic validation rules.
6. Enforce hard block on un-reviewed PII exports (HTTP 400).
7. No external deployment or data transmission.
8. State only empirical security compliance evidence.
