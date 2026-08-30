# Reusable Skill: Document Quality Assurance

- **Purpose**: Analyze input image contrast, blur, skew, and resolution, routing unreadable documents to `rescan_required`.
- **Human Approval Boundary**: Quality thresholds and rescan triggers must be approved by Victor Sabo.
- **Input Files**: `data/synthetic/*`, `app/shared/schemas.py`
- **Output Files**: `app/backend/agents/quality_agent.py`
- **Permitted Actions**: Quality metric calculation (Laplacian variance, brightness/contrast), rescan status assignment.
- **Prohibited Actions**: Allowing unreadable or corrupt documents to proceed to extraction without quality warning.
- **Tests & Evidence Required**: `python tests/test_pipeline.py` (Extreme Hard Case Rescan Routing Test PASS).
- **Escalation Conditions**: Extreme image corruption, unreadable file header.
- **Trajectory Capture Required**: `Yes` (`.agent/workflows/` / `logs/`).

---

## 🛡️ Mandatory Safety Directives
1. Synthetic image inputs only.
2. Zero handwriting hallucination.
3. Attach visual bounding box crop evidence coordinates.
4. Separate quality assessment from downstream field verification.
5. Apply deterministic quality threshold rules first.
6. Trigger mandatory rescan routing on unreadable document scans.
7. No external deployment.
8. State only empirical test evidence.
