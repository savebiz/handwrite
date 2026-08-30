# Reusable Skill: Hackathon Evidence

- **Purpose**: Capture agent execution trajectories, comparative evaluation tables, hard-case analysis, and presentation video plans.
- **Human Approval Boundary**: Hackathon evidence assets and video plans must be approved by Victor Sabo.
- **Input Files**: `outputs/evaluation_results.json`, `docs/*`
- **Output Files**: `docs/agent-trajectories.md`, `docs/hard-case-analysis.md`, `docs/video-plan.md`
- **Permitted Actions**: Trajectory logging, empirical accuracy reporting, video script outlining.
- **Prohibited Actions**: Publishing unbacked accuracy claims or modifying test logs to fabricate evidence.
- **Tests & Evidence Required**: Empirical metric verification against `outputs/evaluation_results.json`.
- **Escalation Conditions**: Missing evaluation log, accuracy discrepancy.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic form data only.
2. Zero handwriting hallucination.
3. Every documented field cites visual crop evidence coordinates.
4. Keep evidence documentation separate from runtime pipeline execution.
5. Apply deterministic validation rules.
6. Emphasize human-in-the-loop review guardrails.
7. No external deployment.
8. State only empirical evaluation metrics recorded directly in `outputs/evaluation_results.json`.
