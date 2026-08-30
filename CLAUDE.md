# CLAUDE.md — Operating Manual for HandWrite Verify

## 👤 Individual Entry Declaration
- **Submission Type**: Individual Challenge Entry (Frontier Engineering Challenge 2026).
- **Participant & Final Decision-Maker**: **Victor Sabo** (`sabo.victor1@gmail.com`).
- **Virtual Agent Roles**: Specialized role definition files located under `.agent/roles/` represent virtual coding-agent roles operated under Victor Sabo's direction to structure agentic execution. This project is **not** a real team submission.
- **Human Authority**: Final approvals, code merges, interpretation of evaluation evidence, dependency decisions, and submission approvals remain 100% human-owned by Victor Sabo.

---

## Product Purpose & MVP Boundaries
HandWrite Verify turns scanned handwritten business forms into structured, evidence-linked, review-ready records without silently treating uncertain handwriting as fact.

### MVP Scope Boundaries
- **Primary Demo Schema**: `field_inspection` forms.
- **Secondary Supported Schema**: `customer_onboarding` forms.
- Input Formats: Synthetic PNG/JPG images and PDFs.
- Human-in-the-Loop Safety: Sensitive/personal data and low-confidence fields MUST be routed to human review.
- **Deferred / Out of Scope**: Custom handwriting OCR model training, live ECM/M-Files integration, production multi-user auth, production deployment, real customer data, batch processing, complex analytics dashboards, pattern memory.

---

## Required Reading Order for Agents
Before taking any ticket or action, agents must read in order:
1. `CLAUDE.md` (this file)
2. `ROADMAP.md`
3. `REVIEW.md`
4. Relevant specifications in `/specs/`
5. Assigned skill in `.agent/skills/`
6. Assigned role in `.agent/roles/`
7. Ticket details in `.agent/workflows/`

---

## Operating Directives

### Plan-First Rule
- For any non-trivial edit or architectural step, formulate a plan and verify alignment.
- Work on one focused ticket per session.

### Action Classification
- **Safe Actions**: Reading files, running unit tests, executing evaluation benchmarks, generating synthetic sample images, updating documentation.
- **Ask-First Actions**: Installing new third-party dependencies, modifying public API contracts, altering core verification policies or confidence thresholds.
- **Human-Owned Actions**: Approving sensitive fields for export, merging code to main, deploying, modifying external system integrations.

---

## Autonomous Loop Budget & Escalation Protocol
- **Maximum 3 implementation iterations per ticket.**
- **Maximum 30 minutes wall-clock per ticket.**
- **Maximum 1 dependency installation attempt without explicit human sign-off.**
- **Immediate Hard Stop**: If a secret/API key leak, destructive command, security vulnerability, real personal data, or ambiguous requirement is detected.
- Create an explicit escalation note in `logs/` rather than guessing or looping endlessly.

---

## Evidence & Verification Rules
- **No Unbacked Claims**: Never state that extraction or accuracy improved without recorded metrics against the identical labelled synthetic dataset.
- **Evidence Reference**: Every extracted field must include source page, bounding box `[ymin, xmin, ymax, xmax]`, and crop path.
- **Audit Logs**: All triage decisions, automated checks, and human reviewer actions must be appended to the immutable audit log (`logs/audit.jsonl`).
