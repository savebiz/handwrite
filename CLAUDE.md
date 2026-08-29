# CLAUDE.md — Operating Manual for HandWrite Verify

## Product Purpose & MVP Boundaries
HandWrite Verify turns scanned handwritten business forms into structured, evidence-linked, review-ready records without silently treating uncertain handwriting as fact.

### MVP Scope Boundaries
- Document Families: `field_inspection` and `customer_onboarding`.
- Input formats: Synthetic PNG/JPG images and PDFs.
- Human-in-the-Loop Safety: Sensitive/personal data and low-confidence fields MUST be routed to human review.
- Out of Scope: Training custom OCR/handwriting neural networks, real customer data, live ECM/M-Files integration, autonomous credit/legal decisions.

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
