# Reusable Skill: Project Coordination

- **Purpose**: Enforce plan-first execution workflows, track roadmap completion, maintain CHANGELOG.md entries, and orchestrate virtual specialist roles.
- **Human Approval Boundary**: All workflow ticket definitions, roadmap priorities, and changelog updates must be approved by Victor Sabo.
- **Input Files**: `CLAUDE.md`, `ROADMAP.md`, `REVIEW.md`, `.agent/workflows/*`
- **Output Files**: `ROADMAP.md`, `CHANGELOG.md`, `docs/virtual-team-operating-model.md`, `docs/agent-handoff-template.md`
- **Permitted Actions**: Ticket definition, roadmap status tracking, handoff verification.
- **Prohibited Actions**: Executing un-planned architectural changes, bypassing human approval boundaries.
- **Tests & Evidence Required**: 100% roadmap alignment audit against `REVIEW.md`.
- **Escalation Conditions**: Scope creep, autonomous loop overflow (>3 iterations), secret leak.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic data only.
2. Zero handwriting value hallucination.
3. Bounding box evidence required for all fields.
4. Separate extraction, verification, triage, and human review stages.
5. Deterministic validation precedes model judgment.
6. Enforce human review for personal/sensitive fields.
7. No external deployment or irreversible actions.
8. Empirical test evidence required for all claims.
