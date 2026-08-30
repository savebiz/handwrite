# Submission Integrity & Work Categorization — HandWrite Verify

This document certifies the origin, work categorization, and individual authenticity of all assets in the HandWrite Verify repository.

---

## 1. Work Categorization Matrix

| Asset Category | File Paths / Locations | Origin & Description |
|---|---|---|
| **Pre-existing Repository Files** | *None* | Workspace was completely empty at challenge initialization. |
| **Challenge-Created Source Code** | `app/backend/`, `app/frontend/`, `app/shared/`, `api/index.py` | Fullstack application written specifically for the Frontier Engineering Challenge 2026. |
| **Challenge-Created Specifications** | `specs/*.md`, `CLAUDE.md`, `ROADMAP.md`, `REVIEW.md` | Data contracts, field dictionaries, and operating directives written during the challenge. |
| **Challenge-Created Agent Governance** | `.agent/roles/*.md`, `.agent/skills/*/SKILL.md`, `.agent/workflows/*.md` | Virtual role definitions and skill workflows developed for agentic execution. |
| **Generated Synthetic Corpus** | `data/synthetic/`, `data/gold-labels/`, `data/manifests/` | 12 synthetic document forms and gold labels generated programmatically via `scripts/generate_synthetic_corpus.py`. |
| **Generated Evaluation Results** | `outputs/evaluation_results.json` | Empirical benchmark results generated via `evaluation/evaluate.py`. |

---

## 2. Integrity & Originality Certification
1. **Individual Entry**: Submitted solely by **Victor Sabo**. No uncredited third-party code or proprietary customer data was imported.
2. **Synthetic Data Policy**: 100% of processed forms are programmatically synthesized. No real PII, credentials, or proprietary documents are contained in this repository.
3. **Reproducibility Guarantee**: All benchmark results can be independently reproduced from scratch using `python scripts/generate_synthetic_corpus.py` and `python evaluation/evaluate.py`.
