# Virtual Specialist Operating Model — HandWrite Verify

This document outlines the operating model governing the virtual specialist coding-agent roles for the **HandWrite Verify** individual challenge submission by **Victor Sabo**.

---

## 👤 Individual Entry & Human Governance
* **Sole Human Participant**: **Victor Sabo** (`sabo.victor1@gmail.com`).
* **Virtual Specialist Roles**: The 10 role definitions located in `.agent/roles/` represent specialized coding-agent capabilities operated strictly under Victor Sabo's direction. This repository is **not** a real team project.
* **Human Approval Boundary**: Final approvals, pull request merges, interpretation of evaluation metrics, dependency approvals, and submission decisions remain 100% human-owned by Victor Sabo.

---

## 🔄 Bounded Delivery Protocol (Plan -> Implement -> Test -> Review -> Document)
Every virtual agent task follows a strict 12-step protocol:

1. **Read Directives**: Inspect `CLAUDE.md`, `ROADMAP.md`, `REVIEW.md`, assigned role file, and assigned skill file.
2. **Plan-First**: Formulate explicit objective, files affected, risks, and completion criteria.
3. **Synthetic Data Policy**: Use synthetic document forms (`data/synthetic/`) only. Never process real customer PII or real paper documents.
4. **No Hallucination**: Every extracted field must link to bounding box evidence coordinates `[ymin, xmin, ymax, xmax]`.
5. **Separation of Stages**: Keep extraction, deterministic verification, triage, and human review decisions strictly separate.
6. **Deterministic-First Validation**: Execute regex patterns, ISO dates, enums, required checks, and cross-field rules BEFORE model judgment.
7. **Human-in-the-Loop Safeguard**: Route low-confidence (<0.85), contradictory, missing, or sensitive/personal fields to human review or rescan.
8. **No Irreversible Actions**: Prohibit production deployment, ECM connector modifications, or destructive database operations.
9. **No Unsupported Claims**: Every accuracy metric must be backed by empirical test logs (`outputs/evaluation_results.json`).
10. **Autonomous Budget**: Max 3 implementation iterations, max 30 minutes wall-clock time per ticket, max 1 dependency install attempt.
11. **Review Checklist**: Audit against 14-point review checklist in `REVIEW.md`.
12. **Structured Handoff**: Emit completed handoff record using [docs/agent-handoff-template.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/agent-handoff-template.md).
