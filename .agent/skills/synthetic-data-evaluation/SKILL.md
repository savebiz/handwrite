# Reusable Skill: Synthetic-Data Evaluation

- **Purpose**: Render synthetic form images, generate ground truth gold labels, and calculate comparative evaluation metrics (Verified Accuracy, Escalation Recall).
- **Human Approval Boundary**: Benchmark scoring algorithm and ground truth datasets must be approved by Victor Sabo.
- **Input Files**: `specs/evaluation-plan.md`, `data/manifests/manifest.json`
- **Output Files**: `scripts/generate_synthetic_corpus.py`, `evaluation/baseline.py`, `evaluation/evaluate.py`, `outputs/evaluation_results.json`
- **Permitted Actions**: Synthetic form rendering, accuracy evaluation execution, JSON metric reporting.
- **Prohibited Actions**: Fabricating accuracy metrics or modifying ground truth gold labels to inflate scores.
- **Tests & Evidence Required**: `python evaluation/evaluate.py` output report saved to `outputs/evaluation_results.json`.
- **Escalation Conditions**: Missing gold label file, scoring algorithm discrepancy.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Programmatically synthesized evaluation data only. Zero real customer documents.
2. Zero handwriting value hallucination.
3. Every test evaluation field carries bounding box crop coordinates.
4. Keep evaluation scoring separate from live agent triage logic.
5. Apply deterministic validation rules.
6. Evaluate human review escalation recall (100% target).
7. No external deployment.
8. State only performance metrics recorded directly in `outputs/evaluation_results.json`.
