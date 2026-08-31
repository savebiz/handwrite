# Final Risk Register — HandWrite Verify

This document catalogs and classifies all identified technical risks, architecture limitations, and operational items for HandWrite Verify.

---

## 🚦 Risk Classification Matrix

| Risk ID | Title / Risk Description | Classification | Impact | Mitigation / Status |
|---|---|---|---|---|
| `RISK-01` | **Severe Image Rotation (> 30°)**: Scanned forms rotated beyond 30° shift target handwriting text outside default schema crops. | **Acceptable Limitation** | Low | Intake Quality Agent detects `row_projection_skew` during pre-screening and routes document status to `RESCAN_REQUIRED`. |
| `RISK-02` | **Local PIL Crop Slicing Fallback**: When commercial VLM vision endpoints are unconfigured, extraction falls back to PIL crop image slicing based on schema templates. | **Acceptable Limitation** | Low | Disclosed design choice enabling 100% local offline reproducibility and $0.00 cloud API costs. |
| `RISK-03` | **Static Bounding Box Schemas**: Target handwriting is expected to align within predefined schema bounding box coordinates in `app/shared/metadata.py`. | **Acceptable Limitation** | Low | Schema metadata dictionary (`metadata.py`) explicitly defines bounding box templates per document schema type. |
| `RISK-04` | **File-Backed JSON Reviewer Store**: Reviewer web UI interacts with local file-backed JSON database store (`outputs/db/`). | **Acceptable Limitation** | Low | Works out-of-the-box locally; persistent volume mount recommended for cloud serverless deployments. |
| `RISK-05` | **Unconstrained Bounding Box Rescaling**: Experimental dynamic crop expansion caused false-positive crop overlaps on tight multi-line tables. | **Should Fix (Resolved)** | None | Removed during controlled experiment 1; documented in `CHANGELOG.md`. |
| `RISK-06` | **PII Export Without Approval**: Potential leak of personal data if sensitive fields are exported without human sign-off. | **Blocker (Mitigated)** | High | Fully mitigated in `app/backend/main.py` (`/export` endpoint returns HTTP 400 if sensitive PII lacks explicit human approval). |

---

## 📌 Summary Breakdown

- **Blockers**: **0 Active Blockers** (All potential export safety blockers fully mitigated)
- **Must Fix**: **0 Items**
- **Should Fix**: **0 Items**
- **Acceptable Limitations**: **4 Disclosed Design Choices** (`RISK-01` through `RISK-04`)
