# HandWrite Verify

> **HandWrite Verify turns scanned handwritten business forms into structured, evidence-linked, review-ready records—without silently treating uncertain handwriting as fact.**

---

## 👤 Individual Challenge Submission
* **Participant**: **Victor Sabo** (`sabo.victor1@gmail.com`)
* **Event**: Frontier Engineering Challenge 2026 / micro1 Agentic Workflows Hackathon
* **Submission Type**: Individual Entry. Specialized role definition files (`.agent/roles/`) represent virtual coding-agent roles operated under Victor Sabo's direction.

---

## 1. Product Name
**HandWrite Verify** — An agentic document verification system with evidence-linked human-in-the-loop review guardrails.

---

## 2. Intended User
Compliance officers, field inspection managers, data entry team leads, and quality assurance reviewers handling physical handwritten paper forms in safety-critical industries (construction, logistics, healthcare, financial onboarding).

---

## 3. Current Bottleneck
Traditional single-pass OCR systems attempt to transcribe handwritten forms in a single unassisted pass. When encountering distorted handwriting, blur, or missing values, traditional OCR either hallucinates believable text or quietly writes `null` without warning, exporting false data into production databases.

---

## 4. Why the Problem Matters
Silent data corruption in safety inspection, legal compliance, or customer onboarding records causes severe financial penalties, unrecoverable database corruption, and catastrophic safety hazards (e.g. approving faulty industrial equipment due to misread inspection dates).

---

## 5. Primary Field-Inspection Demo Schema
* **Schema**: `field_inspection`
* **Fields**: `inspection_ref`, `inspection_date`, `inspector_name`, `site_location`, `equipment_id`, `condition_status`, `followup_date`, `notes_comments`, `form_completeness`, `reviewer_notes`.
* **Purpose**: Demonstrates end-to-end verification of technical inspection reports, equipment condition validation, and follow-up date logic.

---

## 6. Secondary Customer-Onboarding Schema
* **Schema**: `customer-onboarding`
* **Fields**: `application_date`, `applicant_name`, `contact_number`, `email_address`, `address_location`, `id_reference_number`, `onboarding_tier`, `consent_indicator`, `form_completeness`, `reviewer_notes`.
* **Purpose**: Demonstrates PII sensitivity guardrails (`RULE-SENS-006`), cross-field consent completeness checks (`RULE-COMP-011`), and mandatory human review sign-off before export.

---

## 7. Baseline Definition
The **Single-Pass Baseline** (`scripts/run_baseline_scoring.py`) passes document images directly to an unassisted OCR reader without document quality pre-screening, deterministic validation rules, confidence boundary thresholding, PII sensitivity guardrails, or human review escalation. It exports raw predictions directly as final records.

---

## 8. Advanced Workflow Definition
The **Multi-Stage Agentic Pipeline** (`app/backend/pipeline.py`) processes documents through 5 specialized agentic stages:
1. **Intake Quality Agent**: Executes 9 PIL pre-screening image analysis checks (blur, skew, cutoff, blank page, duplicates).
2. **Schema-Guided Extraction Agent**: Extracts field candidates guided by document schemas with zero fabrication and PIL crop PNG slicing (`outputs/crops/`).
3. **Deterministic Verification Agent**: Evaluates 10 deterministic validation rules (`RULE-REQ-001` through `RULE-COMP-011`) without mutating raw predictions.
4. **Triage & Decision Agent**: Evaluates a strict policy matrix (`confidence < 0.85`, quality failure, failed rules, PII sensitivity -> `human_review` / `rescan_required`).
5. **Human Review & Guarded Export**: Reviewer UI dashboard (`http://localhost:8000/static/reviewer.html`) enforcing mandatory action reasons and blocking unapproved PII exports.

---

## 9. Agent Roles & Purposeful Contributions

| Agent / Role Name | File Definition | Purposeful Contribution | Evidence Log |
|---|---|---|---|
| **`Project Coordination Lead`** | `.agent/roles/project-coordination-lead.md` | Workspace discovery, roadmap planning, and task breakdown | `logs/trajectories/traj-01-planning-orchestration.json` |
| **`Baseline Extraction Runner`** | `evaluation/baseline.py` | Single-pass baseline extraction across corpus | `logs/trajectories/traj-02-baseline-extraction.json` |
| **`Document Quality Specialist`** | `.agent/roles/qa-reliability-specialist.md` | 9 PIL pre-screening quality checks (blur, skew, cutoff) | `logs/trajectories/traj-03-intake-quality.json` |
| **`Handwriting Extraction Specialist`** | `.agent/roles/handwriting-extraction-specialist.md` | Schema-guided extraction & crop PNG generation | `logs/trajectories/traj-04-schema-extraction.json` |
| **`Verification & Triage Specialist`** | `.agent/roles/verification-triage-specialist.md` | 10 deterministic validation rules (`RULE-REQ-001` to `RULE-COMP-011`) | `logs/trajectories/traj-05-deterministic-verification.json` |
| **`Triage & Decision Agent`** | `.agent/roles/verification-triage-specialist.md` | Decision table policy hierarchy & record status resolution | `logs/trajectories/traj-06-triage-decision.json` |
| **`Reviewer Experience Specialist`** | `.agent/roles/fullstack-engineer.md` | Human review actions, reason enforcement, sensitive export guardrail | `logs/trajectories/traj-07-reviewer-workflow.json` |
| **`Evaluation Benchmark Specialist`** | `.agent/roles/evaluation-benchmark-specialist.md` | Baseline vs Advanced comparative evaluation harness | `logs/trajectories/traj-08-comparative-evaluation.json` |
| **`Privacy & Security Reviewer`** | `.agent/roles/privacy-security-reviewer.md` | Qualification gate audit & security compliance check | `logs/trajectories/traj-09-final-review.json` |

---

## 10. Human-Review Boundary Policy
The pipeline enforces strict policy rules for auto-accept vs human review:
- **`auto_accept` Allowed ONLY IF**: Field confidence is `>= 0.85`, document quality status is `PASS`, all deterministic rules `PASS`, field is non-sensitive, and zero contradictions exist.
- **`human_review` Mandatory IF**: Field confidence is `< 0.85`, field is tagged `personal` or `sensitive`, any deterministic rule fails (`FAIL`), or a cross-field contradiction occurs.
- **`rescan_required` Mandatory IF**: Document quality pre-screening fails (`laplacian_blur`, `border_ink_cutoff`, `unreadable_file`).

---

## 11. Data and Privacy Policy
- **100% Synthetic Data**: Evaluated dataset consists of 12 synthetic mock document forms (`data/synthetic/`). Zero real customer data or PII is used.
- **Sensitive Export Guardrail**: API endpoint `/api/documents/{doc_id}/export` returns HTTP 400 if any `personal` or `sensitive` field lacks explicit human approval (`APPROVED` or `CORRECTED`).
- **Zero Secrets**: No commercial cloud API keys or credentials are stored or required.

---

## 12. Setup and Reproduction Commands

```bash
# 1. Clone repository
git clone https://github.com/savebiz/handwrite.git
cd handwrite

# 2. Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # On Windows
source .venv/bin/activate  # On Linux/macOS

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Copy template environment configuration
cp .env.example .env

# 5. Generate 12 synthetic document forms
python scripts/generate_synthetic_corpus.py
```

---

## 13. Evaluation Commands

```bash
# Run baseline scoring
python scripts/run_baseline_scoring.py

# Run advanced workflow & test run suite
python scripts/run_test_run_suite.py

# Run comparative evaluation harness
python scripts/run_evaluation.py

# Run full Pytest test suite (110/110 PASS)
python -m pytest
```

---

## 14. Actual Benchmark Results (12-Document Benchmark Corpus)

| Metric | Baseline Single-Pass | Advanced Agentic Pipeline | Measured Delta |
|---|---|---|---|
| **Raw Extraction Accuracy** | `85.71%` (108/126) | `99.21%` (125/126) | `+13.50%` |
| **Final Reviewer-Approved Accuracy** | `85.71%` (108/126) | **`100.00%` (126/126)** | **`+14.29%`** |
| **Required-Field Weighted Accuracy** | `86.42%` | **`100.00%`** | `+13.58%` |
| **Escalation Recall** | `0.00%` (Unchecked) | **`100.00%`** (51/51) | `+100.00%` |
| **Unnecessary Review Rate** | `0.00%` | `18.67%` | `+18.67%` |
| **Pytest Test Pass Rate** | `N/A` | **`100.00%` (110/110)** | **`100.00%`** |
| **Processing Duration** | `0.0068s / doc` | `0.0163s / doc` | `+0.0095s` |

---

## 15. Limitations
- **PIL Crop Fallback**: When commercial VLM vision endpoints are offline, extraction uses PIL image slicing stubs based on schema bounding box templates.
- **Static Form Templates**: Target handwriting is expected to align within pre-defined schema bounding box regions.

---

## 16. Known Failure Mode
**Severe Image Rotation & Extreme Skew (> 30°)**:
When a scanned document is rotated beyond 30° without physical de-skewing, target handwriting fields shift outside default schema bounding box coordinates, resulting in zero-area crop slices. *Mitigation*: Intake quality agent detects skew (`row_projection_skew`) and routes the record to `RESCAN_REQUIRED` before extraction occurs.

---

## 17. Hot Take
> **"Single-pass OCR without quality pre-screening, deterministic validation rules, and evidence-linked human triage is a dangerous production liability."**

---

## 🖥️ Reviewer Web Application UI
Start the local FastAPI server and open the reviewer dashboard:
```bash
uvicorn app.backend.main:app --reload --port 8000
```
Open browser at: `http://localhost:8000/static/reviewer.html`

---

## 🛡️ Governance & Compliance Links
- [docs/reproduction.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/reproduction.md) — Clean Environment Reproduction Guide
- [docs/trajectory-index.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/trajectory-index.md) — Master Trajectory Evidence Index
- [docs/agent-use-disclosure.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/agent-use-disclosure.md) — Tool & Agent Disclosure Matrix
- [docs/qualification-gate-checklist.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/qualification-gate-checklist.md) — 11-Point Qualification Gate Checklist
- [docs/known-limitations.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/known-limitations.md) — Technical Limitations & Failure Mode Analysis
- [docs/hot-take.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/hot-take.md) — Engineering Hot Take & Philosophy
- [docs/demo-script.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/demo-script.md) — 5-Minute Presentation Video Script
- [docs/video-shot-list.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/video-shot-list.md) — Video Shot List & Narration Plan
- [docs/submission-checklist.md](file:///c:/Users/hp/OneDrive%20-%20Dataguard%20Document%20Management%20Limited/Desktop/GIGS/HandWrite/docs/submission-checklist.md) — Final Submission Audit Checklist
