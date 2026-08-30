# Reusable Skill: Reproducibility

- **Purpose**: Provide clean-environment setup instructions, programmatic synthetic data generation, and automated evaluation reproduction.
- **Human Approval Boundary**: Reproduction guides and clean installation steps must be approved by Victor Sabo.
- **Input Files**: `requirements.txt`, `app/frontend/package.json`, `scripts/generate_synthetic_corpus.py`
- **Output Files**: `docs/reproduction.md`, `docs/qualification-gate-checklist.md`
- **Permitted Actions**: Writing reproduction guides, testing clean environment setups, verifying command execution.
- **Prohibited Actions**: Publishing unbacked setup steps or omitting required dependency files.
- **Tests & Evidence Required**: Clean installation verification (`pip install -r requirements.txt`).
- **Escalation Conditions**: Failed dependency resolution, missing setup file, command execution error.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic evaluation data only.
2. Zero handwriting hallucination in setup examples.
3. Include bounding box evidence coordinates in all reproduction examples.
4. Separate setup instructions from core processing code.
5. Apply deterministic validation rules.
6. Emphasize human-in-the-loop review guardrails.
7. No external deployment.
8. State only empirical evaluation metrics recorded in `outputs/evaluation_results.json`.
